# backend/main.py

# PREDATA PROJECT FastAPI Backend


from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import pickle
import torch
import torch.nn as nn
import sys
import os

# Add parent folder to path so we can import our model class
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(
    title="PreData API",
    description="AI-Based Microclimate Prediction & Crop Recommendation System",
    version="1.0.0"
)

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. LOAD ALL SAVED MODELS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Load Random Forest model
with open(os.path.join(MODELS_DIR, "rf_crop_model.pkl"), "rb") as f:
    rf_model = pickle.load(f)

# Load Label Encoder
with open(os.path.join(MODELS_DIR, "label_encoder.pkl"), "rb") as f:
    label_encoder = pickle.load(f)

# Load Scaler
with open(os.path.join(MODELS_DIR, "scaler.pkl"), "rb") as f:
    scaler = pickle.load(f)

# Load LSTM Model
class WeatherLSTM(nn.Module):
    def __init__(self, input_size, hidden_size=64, num_layers=2, output_size=2):
        super(WeatherLSTM, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size,
                            num_layers=num_layers,
                            batch_first=True,
                            dropout=0.2)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return out

lstm_model = WeatherLSTM(input_size=11)
lstm_model.load_state_dict(torch.load(
    os.path.join(MODELS_DIR, "lstm_weather_model.pth"),
    map_location=torch.device("cpu")
))
lstm_model.eval()

print(" All models loaded successfully!")

# INPUT SCHEMAS

class CropInput(BaseModel):
    N: float            # Nitrogen
    P: float            # Phosphorus
    K: float            # Potassium
    temperature: float
    humidity: float
    ph: float
    rainfall: float

class WeatherInput(BaseModel):
    temp_avg: float
    temp_max: float
    temp_min: float
    humidity: float
    rainfall: float
    solar_radiation: float
    wind_speed: float
    soil_moisture: float
    month: int
    day_of_year: int
    is_rainy_season: int

# 3. API ENDPOINTS


@app.get("/")
def home():
    return {
        "message": "Welcome to PreData API 🌱",
        "version": "1.0.0",
        "endpoints": {
            "crop_recommendation": "/predict/crop",
            "weather_prediction":  "/predict/weather",
            "health_check":        "/health"
        }
    }

@app.get("/health")
def health():
    return {"status": "running", "models_loaded": True}


# ---- CROP RECOMMENDATION ENDPOINT ----
@app.post("/predict/crop")
def predict_crop(data: CropInput):
    try:
        input_df = pd.DataFrame([{
            "N":           data.N,
            "P":           data.P,
            "K":           data.K,
            "temperature": data.temperature,
            "humidity":    data.humidity,
            "ph":          data.ph,
            "rainfall":    data.rainfall
        }])

        prediction    = rf_model.predict(input_df)
        crop_name     = label_encoder.inverse_transform(prediction)[0]
        probabilities = rf_model.predict_proba(input_df)[0]
        confidence    = round(float(max(probabilities)) * 100, 2)

        # NPK recommendation based on crop
        npk_guide = {
            "maize":       {"N": "120 kg/ha", "P": "60 kg/ha",  "K": "40 kg/ha"},
            "rice":        {"N": "100 kg/ha", "P": "50 kg/ha",  "K": "50 kg/ha"},
            "chickpea":    {"N": "20 kg/ha",  "P": "60 kg/ha",  "K": "40 kg/ha"},
            "kidneybeans": {"N": "25 kg/ha",  "P": "60 kg/ha",  "K": "40 kg/ha"},
            "banana":      {"N": "200 kg/ha", "P": "60 kg/ha",  "K": "300 kg/ha"},
            "mango":       {"N": "100 kg/ha", "P": "50 kg/ha",  "K": "100 kg/ha"},
            "coffee":      {"N": "150 kg/ha", "P": "30 kg/ha",  "K": "150 kg/ha"},
        }

        npk = npk_guide.get(crop_name, {
            "N": "Consult local agronomist",
            "P": "Consult local agronomist",
            "K": "Consult local agronomist"
        })

        return {
            "recommended_crop": crop_name,
            "confidence":       f"{confidence}%",
            "npk_recommendation": npk,
            "input_received":   data.dict()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- WEATHER PREDICTION ENDPOINT ----
@app.post("/predict/weather")
def predict_weather(data: WeatherInput):
    try:
        input_data = [[
            data.temp_avg, data.temp_max, data.temp_min,
            data.humidity, data.rainfall, data.solar_radiation,
            data.wind_speed, data.soil_moisture,
            data.month, data.day_of_year, data.is_rainy_season
        ]]

        # Create 30-day sequence by repeating input
        sequence = np.array(input_data * 30).reshape(1, 30, 11)
        scaled_seq = scaler.transform(
            np.array(input_data * 30)
        ).reshape(1, 30, 11)

        tensor_input = torch.FloatTensor(scaled_seq)

        with torch.no_grad():
            prediction = lstm_model(tensor_input)
            pred_np = prediction.numpy()[0]

        return {
            "predicted_temperature": round(float(pred_np[0]) * 50, 2),
            "predicted_rainfall": round(float(pred_np[1]) * 300, 2),
            "unit_temperature": "°C",
            "unit_rainfall": "mm",
            "input_received": data.dict()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- CROP INTELLIGENCE ENDPOINT ----
class CropQuery(BaseModel):
    crop_name: str
    state: str = "Nigeria"

@app.post("/predict/crop-intelligence")
def crop_intelligence(data: CropQuery):
    try:
        # Crop database — worldwide crops
        crop_db = {
            "maize": {
                "planting_period": "March - April (South), May - June (North)",
                "harvest_period": "July - August (South), Oct - November (North)",
                "growing_days": "90 - 120 days",
                "rainfall_needed": "500 - 800mm per season",
                "temperature": "18°C - 32°C",
                "soil_type": "Well drained loamy soil, pH 5.5 - 7.0",
                "fertilizer": {
                    "N": "120 kg/ha",
                    "P": "60 kg/ha",
                    "K": "40 kg/ha",
                    "application": "Apply NPK at planting, top dress with Urea at 4-6 weeks"
                },
                "common_diseases": [
                    {"name": "Maize Streak Virus", "cure": "Use resistant varieties, control leafhopper with Cypermethrin"},
                    {"name": "Northern Leaf Blight", "cure": "Apply Mancozeb fungicide, use resistant varieties"},
                    {"name": "Stalk Rot", "cure": "Improve drainage, apply Carbendazim fungicide"},
                ],
                "pesticides": [
                    {"pest": "Fall Armyworm", "pesticide": "Emamectin Benzoate or Chlorpyrifos"},
                    {"pest": "Stem Borer", "pesticide": "Carbofuran granules at whorl stage"},
                ],
                "yield_per_ha": "2.5 - 4.0 tonnes",
                "market_price": "₦280,000 per tonne",
            },
            "rice": {
                "planting_period": "May - June (rainy season), Dec - Jan (dry season irrigation)",
                "harvest_period": "October - November (rainy), April - May (dry)",
                "growing_days": "110 - 150 days",
                "rainfall_needed": "1000 - 2000mm per season",
                "temperature": "20°C - 35°C",
                "soil_type": "Clay or clay loam, pH 5.5 - 6.5",
                "fertilizer": {
                    "N": "100 kg/ha",
                    "P": "50 kg/ha",
                    "K": "50 kg/ha",
                    "application": "Split N application — half at transplanting, half at tillering"
                },
                "common_diseases": [
                    {"name": "Rice Blast", "cure": "Apply Tricyclazole fungicide, use resistant varieties"},
                    {"name": "Bacterial Leaf Blight", "cure": "Use copper-based bactericide, avoid excess nitrogen"},
                ],
                "pesticides": [
                    {"pest": "Rice Bug", "pesticide": "Malathion or Lambda-cyhalothrin"},
                    {"pest": "Stem Borer", "pesticide": "Fipronil or Cartap hydrochloride"},
                ],
                "yield_per_ha": "2.0 - 5.0 tonnes",
                "market_price": "₦450,000 per tonne",
            },
            "cassava": {
                "planting_period": "March - April (beginning of rains)",
                "harvest_period": "12 - 18 months after planting",
                "growing_days": "360 - 540 days",
                "rainfall_needed": "1000 - 1500mm per year",
                "temperature": "25°C - 35°C",
                "soil_type": "Sandy loam, well drained, pH 5.5 - 6.5",
                "fertilizer": {
                    "N": "60 kg/ha",
                    "P": "40 kg/ha",
                    "K": "80 kg/ha",
                    "application": "Apply at 4-6 weeks after planting"
                },
                "common_diseases": [
                    {"name": "Cassava Mosaic Disease", "cure": "Use virus-free stems, whitefly control with Imidacloprid"},
                    {"name": "Cassava Brown Streak", "cure": "Use resistant varieties, rogue infected plants"},
                    {"name": "Root Rot", "cure": "Improve drainage, treat with Metalaxyl fungicide"},
                ],
                "pesticides": [
                    {"pest": "Whitefly", "pesticide": "Imidacloprid or Thiamethoxam"},
                    {"pest": "Mealybug", "pesticide": "Dimethoate or biological control with Anagyrus lopezi"},
                ],
                "yield_per_ha": "8 - 15 tonnes",
                "market_price": "₦120,000 per tonne",
            },
            "tomato": {
                "planting_period": "October - November (dry season), April - May (rainy season)",
                "harvest_period": "60 - 90 days after transplanting",
                "growing_days": "60 - 90 days",
                "rainfall_needed": "600 - 1200mm, irrigation recommended",
                "temperature": "18°C - 29°C",
                "soil_type": "Well drained loamy soil, pH 6.0 - 6.8",
                "fertilizer": {
                    "N": "150 kg/ha",
                    "P": "100 kg/ha",
                    "K": "150 kg/ha",
                    "application": "Apply calcium nitrate at fruiting stage to prevent blossom end rot"
                },
                "common_diseases": [
                    {"name": "Early Blight", "cure": "Apply Chlorothalonil or Mancozeb fungicide every 7-10 days"},
                    {"name": "Late Blight", "cure": "Apply Metalaxyl + Mancozeb, remove infected plants"},
                    {"name": "Fusarium Wilt", "cure": "Use resistant varieties, soil solarization"},
                ],
                "pesticides": [
                    {"pest": "Tomato Fruitworm", "pesticide": "Spinosad or Bacillus thuringiensis (Bt)"},
                    {"pest": "Aphids", "pesticide": "Imidacloprid or insecticidal soap"},
                    {"pest": "Whitefly", "pesticide": "Thiamethoxam or neem oil"},
                ],
                "yield_per_ha": "15 - 30 tonnes",
                "market_price": "₦350,000 per tonne",
            },
            "yam": {
                "planting_period": "February - March",
                "harvest_period": "August - October (7-8 months)",
                "growing_days": "210 - 270 days",
                "rainfall_needed": "1000 - 1500mm per season",
                "temperature": "25°C - 30°C",
                "soil_type": "Deep well drained sandy loam, pH 5.5 - 6.5",
                "fertilizer": {
                    "N": "80 kg/ha",
                    "P": "40 kg/ha",
                    "K": "100 kg/ha",
                    "application": "Apply at 6-8 weeks after emergence"
                },
                "common_diseases": [
                    {"name": "Yam Mosaic Virus", "cure": "Use virus-free seed yams, control aphid vectors"},
                    {"name": "Dry Rot", "cure": "Treat seed yams with Thiram before planting"},
                    {"name": "Anthracnose", "cure": "Apply Mancozeb or Copper oxychloride fungicide"},
                ],
                "pesticides": [
                    {"pest": "Yam Beetle", "pesticide": "Aldrin dust or Chlorpyrifos"},
                    {"pest": "Scale Insects", "pesticide": "White oil emulsion or Malathion"},
                ],
                "yield_per_ha": "5 - 15 tonnes",
                "market_price": "₦200,000 per tonne",
            },
        }

        # Search for crop (case insensitive)
        crop_key = data.crop_name.lower().strip()
        
        # Check exact match first
        if crop_key in crop_db:
            result = crop_db[crop_key]
            return {
                "crop": data.crop_name,
                "found": True,
                "state": data.state,
                "data": result
            }
        
        # Check partial match
        for key in crop_db:
            if crop_key in key or key in crop_key:
                result = crop_db[key]
                return {
                    "crop": key.title(),
                    "found": True,
                    "state": data.state,
                    "data": result
                }

        return {
            "crop": data.crop_name,
            "found": False,
            "message": f"Crop '{data.crop_name}' not in database yet. Currently supported: {', '.join(crop_db.keys())}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # ---- USSD ENDPOINT ----
from fastapi import Form

@app.post("/ussd")
async def ussd(
    sessionId:   str = Form(...),
    phoneNumber: str = Form(...),
    text:        str = Form("")
):
    inputs = text.split("*") if text else []
    level  = len(inputs)

    response = ""

    if text == "":
        response = (
            "CON Welcome to AgroSense NG\n"
            "AI Farm Assistant\n\n"
            "1. Crop Recommendation\n"
            "2. Crop Planting Guide\n"
            "3. Weather Forecast\n"
            "4. About AgroSense NG\n"
            "0. Exit"
        )

    elif text == "1":
        response = "CON Crop Recommendation\nEnter Nitrogen (N) level:\n(e.g. 90)"

    elif text == "2":
        response = (
            "CON Crop Planting Guide\n"
            "Select crop:\n\n"
            "1. Maize\n"
            "2. Rice\n"
            "3. Cassava\n"
            "4. Tomato\n"
            "5. Yam"
        )

    elif text == "3":
        response = "CON Weather Forecast\nEnter current temperature (C):\n(e.g. 27)"

    elif text == "4":
        response = (
            "END AgroSense NG v1.0\n"
            "AI Farm Assistant\n"
            "By: Adebayo Mayowa Philip\n"
            "SQI College of ICT\n"
            "Accuracy: 99.55%\n"
            "Coverage: 36 States"
        )

    elif text == "0":
        response = "END Thank you for using AgroSense NG!\nDial *384*1# anytime."

    elif inputs[0] == "1" and level == 2:
        response = "CON Enter Phosphorus (P) level:\n(e.g. 42)"

    elif inputs[0] == "1" and level == 3:
        response = "CON Enter Potassium (K) level:\n(e.g. 43)"

    elif inputs[0] == "1" and level == 4:
        response = "CON Enter Temperature (C):\n(e.g. 27)"

    elif inputs[0] == "1" and level == 5:
        response = "CON Enter Humidity (%):\n(e.g. 80)"

    elif inputs[0] == "1" and level == 6:
        response = "CON Enter Soil pH:\n(e.g. 6.5)"

    elif inputs[0] == "1" and level == 7:
        response = "CON Enter Rainfall (mm):\n(e.g. 200)"

    elif inputs[0] == "1" and level == 8:
        N, P, K = inputs[1], inputs[2], inputs[3]
        temp, humidity, ph, rainfall = inputs[4], inputs[5], inputs[6], inputs[7]
        try:
            input_df = pd.DataFrame([{
                "N": float(N), "P": float(P), "K": float(K),
                "temperature": float(temp),
                "humidity": float(humidity),
                "ph": float(ph),
                "rainfall": float(rainfall)
            }])
            prediction    = rf_model.predict(input_df)
            crop_name     = label_encoder.inverse_transform(prediction)[0]
            probabilities = rf_model.predict_proba(input_df)[0]
            confidence    = round(float(max(probabilities)) * 100, 2)
            npk_guide = {
                "maize":       {"N": "120 kg/ha", "P": "60 kg/ha", "K": "40 kg/ha"},
                "rice":        {"N": "100 kg/ha", "P": "50 kg/ha", "K": "50 kg/ha"},
                "chickpea":    {"N": "20 kg/ha",  "P": "60 kg/ha", "K": "40 kg/ha"},
                "kidneybeans": {"N": "25 kg/ha",  "P": "60 kg/ha", "K": "40 kg/ha"},
                "banana":      {"N": "200 kg/ha", "P": "60 kg/ha", "K": "300 kg/ha"},
                "mango":       {"N": "100 kg/ha", "P": "50 kg/ha", "K": "100 kg/ha"},
                "coffee":      {"N": "150 kg/ha", "P": "30 kg/ha", "K": "150 kg/ha"},
            }
            npk = npk_guide.get(crop_name, {"N": "See agronomist", "P": "See agronomist", "K": "See agronomist"})
            response = (
                f"END Recommended: {crop_name.upper()}\n"
                f"Confidence: {confidence}%\n"
                f"N: {npk['N']}\n"
                f"P: {npk['P']}\n"
                f"K: {npk['K']}"
            )
        except Exception as e:
            response = f"END Error: {str(e)}"

    elif inputs[0] == "2" and level == 2:
        crops = {"1": "maize", "2": "rice", "3": "cassava", "4": "tomato", "5": "yam"}
        crop  = crops.get(inputs[1], "maize")
        crop_db = {
            "maize":   {"plant": "Mar-Apr (South), May-Jun (North)", "harvest": "Jul-Aug",    "price": "N280,000/tonne"},
            "rice":    {"plant": "May-Jun (rainy)",                  "harvest": "Oct-Nov",    "price": "N450,000/tonne"},
            "cassava": {"plant": "Mar-Apr",                          "harvest": "12-18 months","price": "N120,000/tonne"},
            "tomato":  {"plant": "Oct-Nov (dry)",                    "harvest": "60-90 days", "price": "N350,000/tonne"},
            "yam":     {"plant": "Feb-Mar",                          "harvest": "Aug-Oct",    "price": "N200,000/tonne"},
        }
        info = crop_db.get(crop, {})
        response = (
            f"END {crop.upper()} Guide\n"
            f"Plant: {info.get('plant','N/A')}\n"
            f"Harvest: {info.get('harvest','N/A')}\n"
            f"Price: {info.get('price','N/A')}"
        )

    elif inputs[0] == "3" and level == 2:
        response = "CON Enter Humidity (%):\n(e.g. 80)"

    elif inputs[0] == "3" and level == 3:
        response = "CON Enter current month (1-12):\n(e.g. 6 for June)"

    elif inputs[0] == "3" and level == 4:
        temp     = inputs[1]
        humidity = inputs[2]
        month    = inputs[3]
        try:
            scaled_seq = scaler.transform(
                [[float(temp), float(temp)+5, float(temp)-5,
                  float(humidity), 5.0, 18.0, 2.5, 3.0,
                  int(month), int(month)*30,
                  1 if int(month) in [4,5,6,7,8,9,10] else 0]] * 30
            ).reshape(1, 30, 11)
            tensor_input = torch.FloatTensor(scaled_seq)
            with torch.no_grad():
                prediction = lstm_model(tensor_input)
                pred_np    = prediction.numpy()[0]
            response = (
                f"END Weather Forecast:\n"
                f"Temperature: {round(float(pred_np[0])*50,1)}C\n"
                f"Rainfall: {round(float(pred_np[1])*300,1)}mm\n"
                f"Plan your farm well!"
            )
        except Exception as e:
            response = f"END Error: {str(e)}"

    else:
        response = (
            "CON Invalid input.\n\n"
            "1. Crop Recommendation\n"
            "2. Crop Planting Guide\n"
            "3. Weather Forecast\n"
            "0. Exit"
        )

    return response