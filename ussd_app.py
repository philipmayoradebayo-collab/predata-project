# ussd_app.py
# ============================================================
# PREDATA PROJECT — USSD Backend for Smallholder Farmers
# ============================================================

from flask import Flask, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

API_URL = "http://127.0.0.1:8000"

def get_crop_recommendation(N, P, K, temperature, humidity, ph, rainfall):
    try:
        response = requests.post(f"{API_URL}/predict/crop", json={
            "N": float(N), "P": float(P), "K": float(K),
            "temperature": float(temperature),
            "humidity": float(humidity),
            "ph": float(ph),
            "rainfall": float(rainfall)
        })
        data = response.json()
        return (
            f"Crop: {data['recommended_crop'].upper()}\n"
            f"Confidence: {data['confidence']}\n"
            f"N: {data['npk_recommendation']['N']}\n"
            f"P: {data['npk_recommendation']['P']}\n"
            f"K: {data['npk_recommendation']['K']}"
        )
    except:
        return "Error getting recommendation"


def get_crop_info(crop_name):
    try:
        response = requests.post(f"{API_URL}/predict/crop-intelligence", json={
            "crop_name": crop_name,
            "state": "Nigeria"
        })
        data = response.json()
        if data.get("found"):
            d = data["data"]
            return (
                f"{crop_name.upper()} Guide:\n"
                f"Plant: {d['planting_period']}\n"
                f"Harvest: {d['harvest_period']}\n"
                f"Yield: {d['yield_per_ha']}\n"
                f"Price: {d['market_price']}"
            )
        return f"Crop {crop_name} not found"
    except:
        return "Error getting crop info"


@app.route("/ussd", methods=["POST"])
def ussd():
    session_id   = request.form.get("sessionId", "")
    phone_number = request.form.get("phoneNumber", "")
    text         = request.form.get("text", "")

    # Split input into steps
    inputs = text.split("*") if text else []
    level  = len(inputs)

    response = ""

    # ---- LEVEL 0 — Main Menu ----
    if text == "":
        response = (
            "CON Welcome to PreData\n"
            "AI Farm Assistant\n\n"
            "1. Crop Recommendation\n"
            "2. Crop Planting Guide\n"
            "3. Weather Forecast\n"
            "4. About PreData\n"
            "0. Exit"
        )

    # ---- LEVEL 1 ----
    elif text == "1":
        response = (
            "CON Crop Recommendation\n"
            "Enter Nitrogen (N) level:\n"
            "(e.g. 90)"
        )

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
        response = (
            "CON Weather Forecast\n"
            "Enter current temperature (C):\n"
            "(e.g. 27)"
        )

    elif text == "4":
        response = (
            "END PreData v1.0\n"
            "AI Farm Assistant\n"
            "By: Adebayo Mayowa Philip\n"
            "SQI College of ICT\n"
            "Accuracy: 99.55%\n"
            "Coverage: 36 States"
        )

    elif text == "0":
        response = "END Thank you for using PreData!\nDial *384*1# anytime."

    # ---- CROP RECOMMENDATION FLOW ----
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
        result = get_crop_recommendation(N, P, K, temp, humidity, ph, rainfall)
        response = f"END {result}"

    # ---- CROP PLANTING GUIDE FLOW ----
    elif inputs[0] == "2" and level == 2:
        crops = {"1": "maize", "2": "rice", "3": "cassava", "4": "tomato", "5": "yam"}
        crop  = crops.get(inputs[1], "maize")
        result = get_crop_info(crop)
        response = f"END {result}"

    # ---- WEATHER FORECAST FLOW ----
    elif inputs[0] == "3" and level == 2:
        response = "CON Enter Humidity (%):\n(e.g. 80)"

    elif inputs[0] == "3" and level == 3:
        response = "CON Enter current month (1-12):\n(e.g. 6 for June)"

    elif inputs[0] == "3" and level == 4:
        temp     = inputs[1]
        humidity = inputs[2]
        month    = inputs[3]
        try:
            res = requests.post(f"{API_URL}/predict/weather", json={
                "temp_avg":        float(temp),
                "temp_max":        float(temp) + 5,
                "temp_min":        float(temp) - 5,
                "humidity":        float(humidity),
                "rainfall":        5.0,
                "solar_radiation": 18.0,
                "wind_speed":      2.5,
                "soil_moisture":   3.0,
                "month":           int(month),
                "day_of_year":     int(month) * 30,
                "is_rainy_season": 1 if int(month) in [4,5,6,7,8,9,10] else 0
            })
            data = res.json()
            response = (
                f"END Weather Forecast:\n"
                f"Temperature: {data['predicted_temperature']}C\n"
                f"Rainfall: {data['predicted_rainfall']}mm\n"
                f"Plan your farm accordingly!"
            )
        except:
            response = "END Error getting forecast.\nPlease try again."

    else:
        response = (
            "CON Invalid input.\n\n"
            "1. Crop Recommendation\n"
            "2. Crop Planting Guide\n"
            "3. Weather Forecast\n"
            "4. About PreData\n"
            "0. Exit"
        )

    return response


if __name__ == "__main__":
    print(" PreData USSD Backend running on port 5001!")
    app.run(debug=True, port=5001)