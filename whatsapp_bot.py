# whatsapp_bot.py
# PREDATA PROJECT — WhatsApp Bot for Smallholder Farmers


from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
import json

app = Flask(__name__)

# Your PreData backend API
API_URL = "http://127.0.0.1:8000"

# HELPER FUNCTIONS

def get_crop_recommendation(N, P, K, temperature, humidity, ph, rainfall):
    try:
        response = requests.post(f"{API_URL}/predict/crop", json={
            "N": float(N),
            "P": float(P),
            "K": float(K),
            "temperature": float(temperature),
            "humidity": float(humidity),
            "ph": float(ph),
            "rainfall": float(rainfall)
        })
        data = response.json()
        return (
            f" *Recommended Crop:* {data['recommended_crop'].upper()}\n"
            f" *Confidence:* {data['confidence']}\n\n"
            f" *Fertilizer Guide (NPK):*\n"
            f"  • Nitrogen: {data['npk_recommendation']['N']}\n"
            f"  • Phosphorus: {data['npk_recommendation']['P']}\n"
            f"  • Potassium: {data['npk_recommendation']['K']}"
        )
    except:
        return " Could not get recommendation. Please try again."


def get_crop_intelligence(crop_name):
    try:
        response = requests.post(f"{API_URL}/predict/crop-intelligence", json={
            "crop_name": crop_name,
            "state": "Nigeria"
        })
        data = response.json()
        if data.get("found"):
            d = data["data"]
            diseases = "\n".join([f"  • {x['name']}: {x['cure']}" 
                                   for x in d["common_diseases"][:2]])
            pesticides = "\n".join([f"  • {x['pest']}: {x['pesticide']}" 
                                     for x in d["pesticides"][:2]])
            return (
                f" *{crop_name.upper()} — Farming Guide*\n\n"
                f" *Planting:* {d['planting_period']}\n"
                f" *Harvest:* {d['harvest_period']}\n"
                f"⏱ *Growing days:* {d['growing_days']}\n"
                f" *Temperature:* {d['temperature']}\n"
                f" *Rainfall:* {d['rainfall_needed']}\n\n"
                f" *Fertilizer:*\n"
                f"  N: {d['fertilizer']['N']} | "
                f"P: {d['fertilizer']['P']} | "
                f"K: {d['fertilizer']['K']}\n\n"
                f" *Diseases & Cures:*\n{diseases}\n\n"
                f" *Pests & Pesticides:*\n{pesticides}\n\n"
                f" *Market Price:* {d['market_price']}\n"
                f" *Yield:* {d['yield_per_ha']}"
            )
        else:
            return f"❌ Crop '{crop_name}' not found. Supported: maize, rice, cassava, tomato, yam"
    except:
        return "❌ Could not get crop info. Please try again."


def get_weather_prediction(temp_avg, humidity, rainfall, month):
    try:
        response = requests.post(f"{API_URL}/predict/weather", json={
            "temp_avg":        float(temp_avg),
            "temp_max":        float(temp_avg) + 5,
            "temp_min":        float(temp_avg) - 5,
            "humidity":        float(humidity),
            "rainfall":        float(rainfall),
            "solar_radiation": 18.0,
            "wind_speed":      2.5,
            "soil_moisture":   3.0,
            "month":           int(month),
            "day_of_year":     int(month) * 30,
            "is_rainy_season": 1 if int(month) in [4,5,6,7,8,9,10] else 0
        })
        data = response.json()
        return (
            f" *Weather Prediction*\n\n"
            f" *Predicted Temperature:* {data['predicted_temperature']}°C\n"
            f" *Predicted Rainfall:* {data['predicted_rainfall']}mm\n\n"
            f" *Tip:* Plan your farming activities accordingly!"
        )
    except:
        return " Could not get weather prediction. Please try again."


# ============================================================
# MAIN MENU
# ============================================================
MAIN_MENU = """🌿 *Welcome to PreData!*
_AI Farm Assistant for Nigerian Farmers_

Reply with a number:
*1* —  Crop Recommendation
*2* —  Crop Planting Guide
*3* —  Weather Prediction
*4* — ℹ About PreData
*0* —  Main Menu"""

# Store user sessions
sessions = {}

# ============================================================
# WHATSAPP WEBHOOK
# ============================================================
@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.values.get("Body", "").strip()
    sender       = request.values.get("From", "")
    resp         = MessagingResponse()
    msg          = resp.message()

    # Get or create session
    if sender not in sessions:
        sessions[sender] = {"step": "menu", "data": {}}

    session = sessions[sender]
    step    = session["step"]
    text    = incoming_msg.lower()

    # ---- MAIN MENU ----
    if text in ["hi", "hello", "start", "menu", "0", "help"]:
        session["step"] = "menu"
        session["data"] = {}
        msg.body(MAIN_MENU)

    # ---- CROP RECOMMENDATION FLOW ----
    elif text == "1" or step == "crop_N":
        if text == "1":
            session["step"] = "crop_N"
            msg.body(
                " *Crop Recommendation*\n\n"
                "I will ask you 7 questions about your soil.\n\n"
                "Question 1/7:\n"
                "What is your soil *Nitrogen (N)* level?\n"
                "_(Enter a number, e.g. 90)_"
            )
        elif step == "crop_N":
            session["data"]["N"] = incoming_msg
            session["step"] = "crop_P"
            msg.body(
                " Got it!\n\n"
                "Question 2/7:\n"
                "What is your soil *Phosphorus (P)* level?\n"
                "_(Enter a number, e.g. 42)_"
            )

    elif step == "crop_P":
        session["data"]["P"] = incoming_msg
        session["step"] = "crop_K"
        msg.body(
            " Got it!\n\n"
            "Question 3/7:\n"
            "What is your soil *Potassium (K)* level?\n"
            "_(Enter a number, e.g. 43)_"
        )

    elif step == "crop_K":
        session["data"]["K"] = incoming_msg
        session["step"] = "crop_temp"
        msg.body(
            " Got it!\n\n"
            "Question 4/7:\n"
            "What is the average *Temperature* in your area (°C)?\n"
            "_(Enter a number, e.g. 27)_"
        )

    elif step == "crop_temp":
        session["data"]["temperature"] = incoming_msg
        session["step"] = "crop_humidity"
        msg.body(
            " Got it!\n\n"
            "Question 5/7:\n"
            "What is the *Humidity* in your area (%)?\n"
            "_(Enter a number, e.g. 80)_"
        )

    elif step == "crop_humidity":
        session["data"]["humidity"] = incoming_msg
        session["step"] = "crop_ph"
        msg.body(
            " Got it!\n\n"
            "Question 6/7:\n"
            "What is your soil *pH* level?\n"
            "_(Enter a number, e.g. 6.5)_"
        )

    elif step == "crop_ph":
        session["data"]["ph"] = incoming_msg
        session["step"] = "crop_rainfall"
        msg.body(
            " Got it!\n\n"
            "Question 7/7:\n"
            "What is the average *Rainfall* in your area (mm)?\n"
            "_(Enter a number, e.g. 200)_"
        )

    elif step == "crop_rainfall":
        session["data"]["rainfall"] = incoming_msg
        session["step"] = "menu"
        d = session["data"]
        result = get_crop_recommendation(
            d["N"], d["P"], d["K"],
            d["temperature"], d["humidity"],
            d["ph"], d["rainfall"]
        )
        msg.body(
            f" *Analysis Complete!*\n\n"
            f"{result}\n\n"
            f"Reply *0* for main menu"
        )

    # ---- CROP INTELLIGENCE FLOW ----
    elif text == "2":
        session["step"] = "crop_intel"
        msg.body(
            "🔍 *Crop Planting Guide*\n\n"
            "Type the name of any crop:\n"
            "_(e.g. maize, rice, cassava, tomato, yam)_"
        )

    elif step == "crop_intel":
        session["step"] = "menu"
        result = get_crop_intelligence(incoming_msg)
        msg.body(f"{result}\n\nReply *0* for main menu")

    # ---- WEATHER PREDICTION FLOW ----
    elif text == "3":
        session["step"] = "weather_temp"
        msg.body(
            " *Weather Prediction*\n\n"
            "Question 1/3:\n"
            "What is today's *Temperature* (°C)?\n"
            "_(e.g. 27)_"
        )

    elif step == "weather_temp":
        session["data"]["temp"] = incoming_msg
        session["step"] = "weather_humidity"
        msg.body(
            " Got it!\n\n"
            "Question 2/3:\n"
            "What is today's *Humidity* (%)?\n"
            "_(e.g. 80)_"
        )

    elif step == "weather_humidity":
        session["data"]["humidity"] = incoming_msg
        session["step"] = "weather_month"
        msg.body(
            " Got it!\n\n"
            "Question 3/3:\n"
            "What *month* is it? (1-12)\n"
            "_(e.g. 6 for June)_"
        )

    elif step == "weather_month":
        session["data"]["month"] = incoming_msg
        session["step"] = "menu"
        d = session["data"]
        result = get_weather_prediction(
            d["temp"], d["humidity"], 5, d["month"]
        )
        msg.body(f"{result}\n\nReply *0* for main menu")

    # ---- ABOUT ----
    elif text == "4":
        session["step"] = "menu"
        msg.body(
            "ℹ️ *About PreData*\n\n"
            "PreData is an AI-powered agricultural assistant "
            "built for Nigerian farmers.\n\n"
            "🎓 Developed by: Adebayo Mayowa Philip\n"
            "🏫 SQI College of ICT\n"
            "📊 Crop Model Accuracy: 99.55%\n"
            "🌍 Coverage: All 36 Nigerian States\n"
            "📡 Data Source: NASA POWER API\n\n"
            "Reply *0* for main menu"
        )

    # ---- DEFAULT ----
    else:
        msg.body(MAIN_MENU)

    return str(resp)


# RUN THE BOT
if __name__ == "__main__":
    print(" PreData WhatsApp Bot is running on port 5000!")
    print("   Waiting for messages from farmers...")
    app.run(debug=True, port=5000)