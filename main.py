import pandas as pd

# GPS data
data = {
    "lat": [17.3850, 17.3855, 17.3860, 17.3865, 17.3870, 17.3875, 17.3880, 17.3885, 17.3890, 17.3895, 17.3900, 17.3905, 17.3910, 17.3915, 17.3920],
    "lon": [78.4867, 78.4870, 78.4875, 78.4880, 78.4885, 78.4890, 78.4895, 78.4900, 78.4905, 78.4910, 78.4915, 78.4920, 78.4925, 78.4930, 78.4935],
    "time": list(range(1,16))
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv("gps_data.csv", index=False)

print("gps_data.csv has been created!")
