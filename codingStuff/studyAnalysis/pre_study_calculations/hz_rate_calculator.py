import pandas as pd

# Read CSV file
df = pd.read_csv("data/hz_test/hz_rate_test03.csv")

# Calculate time differences between consecutive samples
df['time_diff'] = df['TIMESTAMP'].diff()

# Drop NaN and calculate mean time difference
mean_time_diff = df['time_diff'].dropna().mean()

# Calculate frequency in Hz
frequency = 1000 / mean_time_diff  # as time-stamps are in milliseconds

print(f"The sampling frequency is approximately {frequency:.2f} Hz")