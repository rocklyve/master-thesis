import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Define the offset measurements for each sensor
offsets = [
    [0.1398738799161734, 0.12009729361444244, 0.012020727928426567],
    [-0.2955718292533547, -0.25600328438216025, -0.06682525793299732],
    [0.1556979493371955, 0.13590599076772847, 0.0548045300045672],
    [0.0489282005868894, 0.037597441889186456, 0.6470199785542192],
    [-0.017318478476497035, 0.22642984709128555, 0.8041015953961868],
    [0.368549685409743, 0.4730356848663746, 0.975676546753423]
]

# Calculate the mean offset for each sensor
mean_offsets = [sum(sensor_offsets) / len(sensor_offsets) for sensor_offsets in offsets]

# Print the mean offsets for each sensor
for i, mean_offset in enumerate(mean_offsets, start=1):
    print(f"Mean Offset Temp{i:02d}: {mean_offset:.6f}")