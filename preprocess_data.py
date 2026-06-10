
import pandas as pd
import numpy as np
import os

os.makedirs("data", exist_ok=True)

def preprocess(city_name):
    filepath = f"data/{city_name.lower()}_raw.csv"
    print(f"\nProcessing {city_name}...")

    # Load raw data
    df = pd.read_csv(filepath, index_col="date", parse_dates=True)
    print(f"  Loaded {len(df)} rows")

    # Step 1 — Replace NASA missing value (-999) with NaN
    df.replace(-999, np.nan, inplace=True)

    # Step 2 — Fill missing values using 7-day rolling average
    df = df.fillna(df.rolling(window=7, min_periods=1).mean())

    # Step 3 — Add useful extra features
    df["month"]          = df.index.month
    df["day_of_year"]    = df.index.dayofyear
    df["is_rainy_season"] = df["month"].apply(
        lambda m: 1 if m in [4, 5, 6, 7, 8, 9, 10] else 0
    )

    # Step 4 — Estimate soil moisture from recent rainfall
    df["soil_moisture"] = df["rainfall"].rolling(window=7).sum() / 7
    df["soil_moisture"] = df["soil_moisture"].fillna(0)
    # Step 5 — Check for remaining missing values
    missing = df.isnull().sum().sum()
    if missing > 0:
        print(f" {missing} missing values remaining — filling with column mean")
        df = df.fillna(df.mean())
    else:
        print(f" No missing values")

    # Save cleaned data
    out_path = f"data/{city_name.lower()}_processed.csv"
    df.to_csv(out_path)
    print(f"  Saved processed data → {out_path}")
    print(f"  Columns: {list(df.columns)}")
    return df

cities = ["Ibadan", "Kano", "Enugu",
     "Abia", "Adamawa", "AkwaIbom", "Anambra", "Bauchi",
    "Bayelsa", "Benue", "Borno", "CrossRiver", "Delta",
    "Ebonyi", "Edo", "Ekiti", "Enugu", "FCT", "Gombe",
    "Imo", "Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi",
    "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger", "Ogun",
    "Ondo", "Osun", "Oyo", "Plateau", "Rivers", "Sokoto",
    "Taraba", "Yobe", "Zamfara"]

for city in cities:
    preprocess(city)

print(" n All cities preprocessed successfully!")
print("Check your /data folder for the _processed.csv files.")