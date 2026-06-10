
# Train Random Forest Fertilizer Model


import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import os

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (accuracy_score, classification_report,
                              confusion_matrix, ConfusionMatrixDisplay)

os.makedirs("models", exist_ok=True)


#  LOAD THE KAGGLE CROP RECOMMENDATION DATASET
df = pd.read_csv("data/Crop_recommendation.csv")
print(f" Dataset loaded: {df.shape}")
print(f"nFirst 5 rows:")
print(df.head())
print(f"nCrops in dataset: {df['label'].unique()}")
print(f"Total crops: {df['label'].nunique()}")


#  FILTER FOR YOUR 3 PROJECT CROPS
target_crops = ["maize", "chickpea", "kidneybeans",
                "rice", "cotton", "coconut", "papaya",
                "orange", "apple", "muskmelon", "watermelon",
                "grapes", "mango", "banana", "pomegranate",
                "lentil", "blackgram", "mothbeans", "mungo",
                "pigeonpeas", "jute", "coffee"]

# Keep all crops but highlight your 3 main ones
print(f" Using full dataset with {df['label'].nunique()} crops")


#  PREPARE FEATURES AND TARGET
features = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
X = df[features]
y = df["label"]

# Encode crop labels to numbers
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Save label encoder for backend use
with open("models/label_encoder.pkl", "wb") as f:
    pickle.dump(le, f)
print(f" Label encoder saved → models/label_encoder.pkl")
print(f"   Crops mapped: {list(le.classes_)}")

# SPLIT DATA — 80% TRAIN, 20% TEST

X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)
print(f" Train size: {X_train.shape}, Test size: {X_test.shape}")
#  TRAIN THE RANDOM FOREST MODEL

print("\nTraining Random Forest model...")

rf_model = RandomForestClassifier(
    n_estimators=100,    # 100 decision trees
    max_depth=10,        # max depth per tree
    random_state=42,
    verbose=1
)

rf_model.fit(X_train, y_train)
print(" Training complete!")


#  EVALUATE THE MODEL
y_pred = rf_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n{'='*50}")
print(f"  MODEL ACCURACY: {accuracy * 100:.2f}%")
print(f"{'='*50}")

print("\nDetailed Classification Report:")
print(classification_report(y_test, y_pred, target_names=le.classes_))


#  FEATURE IMPORTANCE — what factors matter most
importances = rf_model.feature_importances_
feat_df = pd.DataFrame({
    "Feature": features,
    "Importance": importances
}).sort_values("Importance", ascending=False)

print("\nFeature Importance (what affects crop recommendation most):")
print(feat_df)

plt.figure(figsize=(8, 5))
plt.barh(feat_df["Feature"], feat_df["Importance"], color="green")
plt.xlabel("Importance Score")
plt.title("Random Forest — Feature Importance for Crop Recommendation")
plt.tight_layout()
plt.savefig("models/rf_feature_importance.png")
plt.show()

# CONFUSION MATRIX

cm = confusion_matrix(y_test, y_pred)
fig, ax = plt.subplots(figsize=(14, 12))
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=le.classes_)
disp.plot(ax=ax, xticks_rotation=45, colorbar=False)
plt.title("Random Forest — Confusion Matrix")
plt.tight_layout()
plt.savefig("models/rf_confusion_matrix.png")
plt.show()

# SAVE THE TRAINED MODEL

with open("models/rf_crop_model.pkl", "wb") as f:
    pickle.dump(rf_model, f)
print("\n Random Forest model saved → models/rf_crop_model.pkl")


# TEST A SAMPLE PREDICTION
print("\n--- Sample Prediction Test ---")
sample = pd.DataFrame([{
    "N": 90, "P": 42, "K": 43,
    "temperature": 27.0,
    "humidity": 80.0,
    "ph": 6.5,
    "rainfall": 200.0
}])

prediction = rf_model.predict(sample)
crop_name = le.inverse_transform(prediction)[0]
print("Input: N=90, P=42, K=43, Temp=27°C, Humidity=80%, pH=6.5, Rainfall=200mm")
print(f" Recommended Crop: {crop_name.upper()}")

print("\n Complete! Random Forest model trained and saved.")