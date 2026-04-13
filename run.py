import pandas as pd
import time
import folium
from sklearn.neighbors import KNeighborsRegressor
import geocoder

# -----------------------------
# STEP 1: LOAD DATA
# -----------------------------
df = pd.read_csv("gps_data.csv")

# Create next location columns
df['next_lat'] = df['lat'].shift(-1)
df['next_lon'] = df['lon'].shift(-1)
df = df.dropna()

# -----------------------------
# STEP 2: TRAIN MODEL
# -----------------------------
X = df[['lat', 'lon']]
y = df[['next_lat', 'next_lon']]

model = KNeighborsRegressor(n_neighbors=2)
model.fit(X, y)

print("Model trained successfully!")

# -----------------------------
# STEP 3: GET CURRENT LOCATION
# -----------------------------
choice = input("Choose location input method:\n1. Manual\n2. Automatic (IP)\nEnter 1 or 2: ")

if choice == "1":
    lat = float(input("Enter latitude: "))
    lon = float(input("Enter longitude: "))
else:
    g = geocoder.ip('me')
    lat, lon = g.latlng
    print("Your approximate location:", lat, lon)

# -----------------------------
# STEP 4: REAL-TIME SIMULATION
# -----------------------------
print("\nStarting real-time tracking simulation...\n")

for idx, row in df.iterrows():
    current_lat, current_lon = row['lat'], row['lon']
    
    # Predict next location
    prediction = model.predict([[current_lat, current_lon]])
    pred_lat, pred_lon = prediction[0]

    # Create map
    m = folium.Map(location=[current_lat, current_lon], zoom_start=15)

    # Current location
    folium.Marker(
        [current_lat, current_lon],
        tooltip="Current Location"
    ).add_to(m)

    # Predicted location
    folium.Marker(
        [pred_lat, pred_lon],
        tooltip="Predicted Location",
        icon=folium.Icon(color='red')
    ).add_to(m)

    # Save map
    m.save("map.html")

    print(f"Current: {current_lat},{current_lon} -> Predicted: {pred_lat},{pred_lon}")

    # Wait to simulate real-time
    time.sleep(2)

print("\nSimulation complete! Open map.html to view results.")
