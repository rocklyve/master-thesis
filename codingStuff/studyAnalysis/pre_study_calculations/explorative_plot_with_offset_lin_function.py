import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np


class ExplorativePlotWithOffsetLinFunction:
    def calibrate(x, y):
        """
       Calibrate one series of temperature readings (x) against another (y).

       Args:
           x (list or numpy array): First series of temperature readings.
           y (list or numpy array): Second series of temperature readings.

       Returns:
           a (float): Slope of the linear fit.
           b (float): Intercept of the linear fit.
       """
        A = np.vstack([x, np.ones(len(x))]).T
        a, b = np.linalg.lstsq(A, y, rcond=None)[0]
        return a, b


    def calibrate2(index):
        # depending on index between 1 and 6, different a and b values should be returned
        #For Temp01: a = 0.9312, b = 2.4677
        #For Temp02: a = 0.9134, b = 2.7736
        #For Temp03: a = 0.9025, b = 3.6064
        #For Temp04: a = 1.1640, b = -5.0952
        #For Temp05: a = 1.0964, b = -3.9971
        #For Temp06: a = 1.0112, b = -0.3162
        # Temp01 is index 1, Temp02 is index 2, ...
        a = [0.9312, 0.9134, 0.9025, 1.1640, 1.0964, 1.0112]
        b = [2.4677, 2.7736, 3.6064, -5.0952, -3.9971, -0.3162]
        return a[index - 1], b[index - 1]


    def execute(self):
        # Read the CSV file into a DataFrame
        # data = pd.read_csv('data/Logging_08_29_Backofen_Metall.csv')
        # data = pd.read_csv('data/Logging_08_26_Offenburg_Boden_Metall.csv')
        data = pd.read_csv('data/Logging_08_29_Ultimaker_35_degree_Metall.csv')
        # data = pd.read_csv('data/Logging_08_29_Ultimaker_40_degree_Metall.csv')
        # data = pd.read_csv('data/Logging_08_29_Ultimaker_45_degree_Metall.csv')

        data = data[100:-100]
        # data2 = data[100:-100]

        # add max timestamp of data to data2
        # data2['TIMESTAMP'] = data['TIMESTAMP'].max() + data2['TIMESTAMP']
        # combine data and data2
        # data = pd.concat([data, data2])

        # Adjust the temperature values by dividing by 100 to get the actual temperature
        temperature_columns = ['Temp01', 'Temp02', 'Temp03', 'Temp04', 'Temp05', 'Temp06']
        temperature_sensor_columns = ['ObjTemp01', 'ObjTemp02', 'ObjTemp03', 'ObjTemp04', 'ObjTemp05', 'ObjTemp06']
        data[temperature_columns] = data[temperature_columns] / 100.0
        data[temperature_columns] = data[temperature_columns].rolling(window=int(len(data.index) / 50),
                                                                      min_periods=int(len(data.index) / 200),
                                                                      center=True).mean()
        data[temperature_sensor_columns] = data[temperature_sensor_columns] / 100.0

        # Create a new column for the average temperature across Temp01-Temp06
        data["MeanTemperature"] = data[temperature_columns].mean(axis=1)

        calibrated_temps = {}
        for col in temperature_columns:
            a, b = calibrate(data[col], data["MeanTemperature"])
            # a, b = calibrate2(int(col[-2:]))
            calibrated_temps[col] = data[col] * a + b
            data[col] = calibrated_temps[col]
            print(f"For {col}: a = {a:.4f}, b = {b:.4f}")

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
        to_plot = [
            "Temp01",
            "Temp02",
            "Temp03",
            "Temp04",
            "Temp05",
            "Temp06",
            "MeanTemperature",
        ]

        lines = plt.plot(data.index, data[
            to_plot
        ])
        # plt.plot(data.index, data['AverageTemp'], color='black', linestyle='dashed', label='Average Temp')

        plt.xlabel('Timestamp')
        plt.ylabel('Temperature (°C)')
        plt.title('Temperature Measurements')
        plt.ylim(data[temperature_columns].min().min(), data[temperature_columns].max().max())  # Set y-axis limits

        # Use AutoDateLocator for automatic x-axis ticks
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5, maxticks=20))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%M:%S'))

        # Add legend for temperature sensors
        plt.legend(lines + [line for line in plt.plot([], [], color='black', linestyle='dashed')], to_plot,
                   loc='upper right')

        # Add phase legend separately
        handles, labels = ax.get_legend_handles_labels()
        unique_labels = list(set(labels))
        # phase_legend = ax.legend([handle for handle, label in zip(handles, labels) if label.startswith('Phase')], unique_labels, loc='upper left')
        # ax.add_artist(phase_legend)

        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('output.png')
        plt.show()

        # terminate program
        exit(0)
        pass
