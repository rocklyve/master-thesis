import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Read the CSV file into a DataFrame
# data = pd.read_csv('data/Logging_08_25_Küchentisch_Metall.csv')
# data = pd.read_csv('data/Logging_08_25_Kühlschrank_Metall.csv')
# data = pd.read_csv('data/Logging_08_28_KühlschrankUndTisch_Metall.csv')
# data = pd.read_csv('data/Logging_08_26_Offenburg_Boden_Metall.csv')
# data = pd.read_csv('data/Logging_08_25_Küchentisch_Metall.csv')
data = pd.read_csv('data/Logging_08_29_Backofen.csv')
# data = data[55000:]
# data = data[10000:]
# data = data[:45000]

# Adjust the temperature values by dividing by 100 to get the actual temperature
temperature_columns = ['Temp01', 'Temp02', 'Temp03', 'Temp04', 'Temp05', 'Temp06']
temperature_sensor_columns = ['ObjTemp01', 'ObjTemp02', 'ObjTemp03', 'ObjTemp04', 'ObjTemp05', 'ObjTemp06']
data[temperature_columns] = data[temperature_columns] / 100.0
data[temperature_columns] = data[temperature_columns].rolling(window=100, min_periods=25, center=True).mean()
data[temperature_sensor_columns] = data[temperature_sensor_columns] / 100.0


# Create a new column for the average temperature across Temp01-Temp06
data['RealTemperature'] = data[['Temp01', 'Temp02', 'Temp03']].mean(axis=1)

# data['Temp01'] += -0.034911
# data['Temp02'] += -0.142163
# data['Temp03'] += 0.177074
# data['Temp04'] += 0.147627
# data['Temp05'] += 0.245508
# data['Temp06'] += 0.506864

# Küchentisch + Kühlschrank mittel metall 1,2,3
data['Temp01'] += -0.045
data['Temp02'] += -0.53
data['Temp03'] += -0.144
data['Temp04'] += 0.25
data['Temp05'] += 0.24
data['Temp06'] += 0.359

# Küchentisch hoch offset
# data['Temp01'] += 0.12127261477536777
# data['Temp02'] += -0.2621983026124006
# data['Temp03'] += 0.14092568783702575
# data['Temp04'] += 0.01745440118097008
# data['Temp05'] += 0.19111562727098885
# data['Temp06'] += 0.43423879157126066

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
# plt.ylim(26, 30)
# plt.ylim(8,10)
# plt.ylim(7, 11)
plt.ylim(30, 47)

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