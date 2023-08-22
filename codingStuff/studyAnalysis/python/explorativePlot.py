import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Read the CSV file into a DataFrame
data = pd.read_csv('Logging.csv')

# Adjust the temperature values by dividing by 100 to get the actual temperature
temperature_columns = ['Temp01', 'Temp02', 'Temp03', 'Temp04', 'Temp05', 'Temp06']
data[temperature_columns] = data[temperature_columns] / 100.0

# Create a new column for the average temperature across Temp01-Temp06
data['AverageTemp'] = data[temperature_columns].mean(axis=1)

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
lines = plt.plot(data.index, data[temperature_columns])
plt.plot(data.index, data['AverageTemp'], color='black', linestyle='dashed', label='Average Temp')

plt.xlabel('Timestamp')
plt.ylabel('Temperature (°C)')
plt.title('Temperature Measurements')
plt.ylim(27, 37)  # Set y-axis limits

# Use AutoDateLocator for automatic x-axis ticks
ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5, maxticks=20))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%M:%S'))

# Add legend for temperature sensors
plt.legend(lines + [line for line in plt.plot([], [], color='black', linestyle='dashed')], temperature_columns + ['Average Temp'], loc='upper right')

# Add phase legend separately
handles, labels = ax.get_legend_handles_labels()
unique_labels = list(set(labels))
phase_legend = ax.legend([handle for handle, label in zip(handles, labels) if label.startswith('Phase')], unique_labels, loc='upper left')
ax.add_artist(phase_legend)

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
