
#  Train LSTM Weather Prediction Model

import pandas as pd  # type: ignore[import-untyped]
import numpy as np
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import os
from torch.utils.data import DataLoader, TensorDataset

os.makedirs("models", exist_ok=True)


# LOAD & COMBINE ALL 36 CITY DATA

cities = ["ibadan", "kano", "enugu",
    "abia", "adamawa", "akwaibom", "anambra", "bauchi",
    "bayelsa", "benue", "borno", "crossriver", "delta",
    "ebonyi", "edo", "ekiti", "enugu", "fct", "gombe",
    "imo", "jigawa", "kaduna", "kano", "katsina", "kebbi",
    "kogi", "kwara", "lagos", "nasarawa", "niger", "ogun",
    "ondo", "osun", "oyo", "plateau", "rivers", "sokoto",
    "taraba", "yobe", "zamfara"
]
frames = []
for city in cities:
    df = pd.read_csv(f"data/{city}_processed.csv", index_col="date", parse_dates=True)
    df["city"] = city
    frames.append(df)

data = pd.concat(frames)
print(f"Loaded combined data: {data.shape}")

#  PREPARE FEATURES — we predict temperature & rainfall
features = ["temp_avg", "temp_max", "temp_min",
            "humidity", "rainfall", "solar_radiation",
            "wind_speed", "soil_moisture",
            "month", "day_of_year", "is_rainy_season"]

target = ["temp_avg", "rainfall"]   # what we want to predict

df_model = data[features].copy()

# Scale data between 0 and 1
scaler = MinMaxScaler()
scaled = scaler.fit_transform(df_model)
scaled_df = pd.DataFrame(scaled, columns=features)

# Save scaler for later use in backend
import pickle
with open("models/scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)
print(" Scaler saved → models/scaler.pkl")


# 3. CREATE SEQUENCES FOR LSTM
# Each sequence = 30 days of data → predict next day

def create_sequences(data, seq_length=30):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])          # 30 days input
        y.append(data[i+seq_length][:2])         # next day temp & rainfall
    return np.array(X), np.array(y)

SEQ_LENGTH = 30
X, y = create_sequences(scaled, SEQ_LENGTH)
print(f" Sequences created: X={X.shape}, y={y.shape}")

# Split into train and test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, shuffle=False
)

# Convert to PyTorch tensors
X_train = torch.FloatTensor(X_train)
X_test  = torch.FloatTensor(X_test)
y_train = torch.FloatTensor(y_train)
y_test  = torch.FloatTensor(y_test)

print(f" Train size: {X_train.shape}, Test size: {X_test.shape}")

#  BUILD THE LSTM MODEL
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
        out = self.fc(out[:, -1, :])   # take last time step
        return out

model = WeatherLSTM(input_size=len(features))
print(f"\n LSTM Model built:")
print(model)

# TRAIN THE MODEL

criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

EPOCHS     = 50
BATCH_SIZE = 512   # process 512 sequences at a time instead of all at once
train_losses = []

# Create data loader
train_dataset = TensorDataset(X_train, y_train)
train_loader  = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)

print("\nTraining started...")
for epoch in range(EPOCHS):
    model.train()
    epoch_loss = 0
    for X_batch, y_batch in train_loader:
        optimizer.zero_grad()
        output = model(X_batch)
        loss   = criterion(output, y_batch)
        loss.backward()
        optimizer.step()
        epoch_loss += loss.item()

    avg_loss = epoch_loss / len(train_loader)
    train_losses.append(avg_loss)

    if (epoch + 1) % 10 == 0:
        print(f"  Epoch {epoch+1}/{EPOCHS} — Loss: {avg_loss:.6f}")

#  EVALUATE THE MODEL

model.eval()
with torch.no_grad():
    predictions = model(X_test)
    test_loss = criterion(predictions, y_test)
    print(f"\n Test Loss (MSE): {test_loss.item():.6f}")

# 7. SAVE THE TRAINED MODEL

torch.save(model.state_dict(), "models/lstm_weather_model.pth")
print("Model saved → models/lstm_weather_model.pth")

# 8. PLOT TRAINING LOSS

plt.figure(figsize=(10, 4))
plt.plot(train_losses, color="blue", label="Training Loss")
plt.title("LSTM Weather Model — Training Loss")
plt.xlabel("Epoch")
plt.ylabel("MSE Loss")
plt.legend()
plt.tight_layout()
plt.savefig("models/lstm_training_loss.png")
plt.close()
print(" Training chart saved  models/lstm_training_loss.png")

print("\nComplete! LSTM model trained and saved.")