import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Read the CSV file into a DataFrame
# data = pd.read_csv('data/Logging_08_25_Boden_hoch.csv')
data = pd.read_csv('data/Logging_08_29_Backofen.csv')
# data = pd.read_csv('data/Logging_08_25_Kühlschrank_Metall.csv')
# data = data[11000:]
# data = data[:25000]

# Adjust the temperature values by dividing by 100 to get the actual temperature
temperature_columns = ['Temp01', 'Temp02', 'Temp03', 'Temp04', 'Temp05', 'Temp06']
temperature_sensor_columns = ['ObjTemp01', 'ObjTemp02', 'ObjTemp03', 'ObjTemp04', 'ObjTemp05', 'ObjTemp06']
data[temperature_columns] = data[temperature_columns] / 100.0
data[temperature_columns] = data[temperature_columns].rolling(window=100, min_periods=25, center=True).mean()
data[temperature_sensor_columns] = data[temperature_sensor_columns] / 100.0


# Create a new column for the average temperature across Temp01-Temp06
data['RealTemperature'] = data[['Temp01', 'Temp02', 'Temp03', 'Temp04', 'Temp05', 'Temp06']].mean(axis=1)

offsets = {}
std_devs = {}
variances = {}
data_means = {}

# Calculate the offset, standard deviation, and variance for each sensor based on the difference from the real temperature mean
for col in temperature_columns:
    data_mean = data[col].mean()
    offset = data['RealTemperature'].mean() - data_mean
    std_dev = data[col].std()
    variance = data[col].var()

    # Store calculated values in the dictionaries
    offsets[col] = offset
    std_devs[col] = std_dev
    variances[col] = variance
    data_means[col] = data_mean

    # here the real offset takes place
    data[col] = data[col] + offset

# Print the grouped output
for col in temperature_columns:
    print('Offset', col, ': ', offsets[col])

print()

for col in temperature_columns:
    print('Data Mean', col, ': ', data_means[col])

print()

for col in temperature_columns:
    print('Std Dev', col, ': ', std_devs[col])

print()

for col in temperature_columns:
    print('Variance', col, ': ', variances[col])

# Set the timestamp as the index (converting from milliseconds to seconds)
data['TIMESTAMP'] = pd.to_datetime(data['TIMESTAMP'], unit='ms')
data.set_index('TIMESTAMP', inplace=True)

# Get unique phase IDs
phase_ids = data['ID'].unique()

# Plotting
plt.figure(figsize=(10, 6))
ax = plt.gca()

# Iterate through phases and add shaded regions
for i, phase_id in enumerate(phase_ids):
    phase_data = data[data['ID'] == phase_id]
    start_timestamp = phase_data.index[0]
    end_timestamp = phase_data.index[-1]
    ax.axvspan(start_timestamp, end_timestamp, facecolor=f'C{i}', alpha=0.2, label=f'Phase {phase_id}')

# Plot temperature data
to_plot = temperature_columns
        # "AverageTempDiff12",
        # "AverageTempDiff13",
        # "AverageTempDiff14",
        # "AverageTempDiff15",
        # "AverageTempDiff16",

     # "AverageTempDiff02",
     # "AverageTempDiff03",
     # "AverageTempDiff04",
     # "AverageTempDiff05",
     # "AverageTempDiff06",

lines = plt.plot(data.index, data[
    to_plot
])
# plt.plot(data.index, data['AverageTemp'], color='black', linestyle='dashed', label='Average Temp')

plt.xlabel('Timestamp')
plt.ylabel('Temperature (°C)')
plt.title('Temperature Measurements')
plt.ylim(30, 47)  # Set y-axis limits
# plt.ylim(6, 25.5)  # Set y-axis limits
# plt.ylim(8.5, 9.5)  # Set y-axis limits

# Use AutoDateLocator for automatic x-axis ticks
ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5, maxticks=20))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%M:%S'))

# Add legend for temperature sensors
plt.legend(lines + [line for line in plt.plot([], [], color='black', linestyle='dashed')], to_plot, loc='upper right')

# Add phase legend separately
handles, labels = ax.get_legend_handles_labels()
unique_labels = list(set(labels))
# phase_legend = ax.legend([handle for handle, label in zip(handles, labels) if label.startswith('Phase')], unique_labels, loc='upper left')
# ax.add_artist(phase_legend)

plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('output.png')
plt.show()