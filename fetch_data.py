
import requests
import pandas as pd
import os
import time

# Make sure the data folder exists
os.makedirs("data", exist_ok=True)

def fetch_farm_data(city_name, lat, lon, start="20150101", end="20231231"):
    """
    Pulls daily climate data for a Nigerian farm location.
    Completely free  no API key needed.
    """
    print(f"Fetching data for {city_name}...")

    url = "https://power.larc.nasa.gov/api/temporal/daily/point"

    params = {
        "parameters": "T2M,T2M_MAX,T2M_MIN,RH2M,PRECTOTCORR,ALLSKY_SFC_SW_DWN,WS2M",
        "community": "AG",
        "longitude": lon,
        "latitude": lat,
        "start": start,
        "end": end,
        "format": "JSON"
    }

    response = requests.get(url, params=params, timeout=60)

    if response.status_code == 200:
        data = response.json()
        props = data["properties"]["parameter"]
        df = pd.DataFrame(props)
        df.index = pd.to_datetime(df.index, format="%Y%m%d")
        df.index.name = "date"
        df.columns = [
            "temp_avg", "temp_max", "temp_min",
            "humidity", "rainfall", "solar_radiation", "wind_speed"
        ]
        # Save to CSV
        filepath = f"data/{city_name.lower()}_raw.csv"
        df.to_csv(filepath)
        print(f"   Saved {len(df)} rows → {filepath}")
        return df
    else:
        print(f"   ERROR {response.status_code} for {city_name}")
        return None


#  Nigerian Farming Locations 
locations = {
    "Ibadan": (7.3775,  3.9470),   # Oyo — maize & cassava
    "Kano":   (12.0022, 8.5920),   # North — grain farming
    "Enugu":  (6.4584,  7.5464),   # South-East — root crops
    "Abia":       (5.4527,  7.5248),
    "Adamawa":    (9.3265,  12.3984),
    "AkwaIbom":   (5.0078,  7.8497),
    "Anambra":    (6.2209,  6.9370),
    "Bauchi":     (10.3158, 9.8442),
    "Bayelsa":    (4.7719,  6.0699),
    "Benue":      (7.3369,  8.7400),
    "Borno":      (11.8333, 13.1500),
    "CrossRiver": (5.8702,  8.5988),
    "Delta":      (5.5200,  5.8987),
    "Ebonyi":     (6.2649,  8.0137),
    "Edo":        (6.3350,  5.6037),
    "Ekiti":      (7.7190,  5.3110),
    "FCT":        (9.0579,  7.4951),
    "Gombe":      (10.2791, 11.1670),
    "Imo":        (5.5720,  7.0588),
    "Jigawa":     (12.2280, 9.5616),
    "Kaduna":     (10.5264, 7.4382),
    "Katsina":    (12.9816, 7.6183),
    "Kebbi":      (12.4539, 4.1975),
    "Kogi":       (7.7337,  6.6906),
    "Kwara":      (8.9669,  4.3874),
    "Lagos":      (6.5244,  3.3792),
    "Nasarawa":   (8.4996,  8.1997),
    "Niger":      (9.9309,  5.5983),
    "Ogun":       (6.9980,  3.4737),
    "Ondo":       (7.2500,  5.2000),
    "Osun":       (7.5629,  4.5200),
    "Oyo":        (7.3775,  3.9470),
    "Plateau":    (9.2182,  9.5179),
    "Rivers":     (4.8156,  7.0498),
    "Sokoto":     (13.0059, 5.2476),
    "Taraba":     (7.9994,  10.7739),
    "Yobe":       (12.2939, 11.7467),
    "Zamfara":    (12.1702, 6.6573),
}

all_data = {}
for city, (lat, lon) in locations.items():
    df = fetch_farm_data(city, lat, lon)
    if df is not None:
        all_data[city] = df
        time.sleep(1) 

print("n All data fetched successfully!")
print("Check your data folder for the CSV files.")