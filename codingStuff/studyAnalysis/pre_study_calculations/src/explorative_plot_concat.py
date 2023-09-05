import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt


# List of CSV files containing measurements
class ExplorativePlotConcat:
    def calibrate_polynomial(self, x, y, degree):
        """
        Calibrate one series of temperature readings (x) against another (y) using a polynomial fit.

        Args:
            x (list or numpy array): First series of temperature readings.
            y (list or numpy array): Second series of temperature readings.
            degree (int): Degree of the polynomial fit.

        Returns:
            coeffs (numpy array): Coefficients of the polynomial fit.
        """
        coeffs = np.polyfit(x, y, degree)
        return coeffs

    def calibrate(self, x, y):
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

    def fetch_data(self, csv_files):
        # Load data from CSV files into separate DataFrames
        data_frames = []
        for file in csv_files:
            file_path = os.path.join(file)  # Update with the actual folder path
            df = pd.read_csv(file_path)
            data_frames.append(df)

        # Concatenate DataFrames vertically
        concatenated_data = pd.concat(data_frames, ignore_index=True)

        # Exclude Time Column from calculations
        concatenated_data = concatenated_data.drop('TIMESTAMP', axis=1)
        return concatenated_data

    def execute(self, plot_name: str):
        csv_files = [
            # 'data/Logging_08_29_Ultimaker_25_degree_Metall.csv',
            # 'data/Logging_08_29_Ultimaker_30_degree_Metall.csv',
            # 'data/Logging_08_29_Ultimaker_35_degree_Metall.csv',
            # 'data/Logging_08_29_Ultimaker_40_degree_Metall.csv',
            # 'data/Logging_08_29_Ultimaker_45_degree_Metall.csv',
            'data/Logging_08_30_Ultimaker_25_degree_Metall.csv',
            'data/Logging_08_30_Ultimaker_30_degree_Metall.csv',
            'data/Logging_08_30_Ultimaker_35_degree_Metall.csv',
            'data/Logging_08_30_Ultimaker_40_degree_Metall.csv',
            'data/Logging_08_30_Ultimaker_45_degree_Metall.csv'
        ]

        temperature_columns = ['Temp01', 'Temp02', 'Temp03', 'Temp04', 'Temp05', 'Temp06']

        data = self.fetch_data(csv_files)
        data[temperature_columns] = data[temperature_columns] / 100.0
        data[temperature_columns] = data[temperature_columns].rolling(window=int(len(data.index) / 50),
                                                                      min_periods=int(len(data.index) / 200),
                                                                      center=True).mean()

        # Create a new column for the average temperature across Temp01-Temp06
        data["MeanTemperature"] = data[temperature_columns].mean(axis=1)

        # calibrated_temps = {}
        # for col in temperature_columns:
        #     a, b = calibrate(data[col], data["MeanTemperature"])
        #     # a, b = calibrate2(int(col[-2:]))
        #     calibrated_temps[col] = data[col] * a + b
        #     data[col] = calibrated_temps[col]
        #     print(f"For {col}: a = {a:.4f}, b = {b:.4f}")

        calibrated_temps = {}
        degree = 2  # Example polynomial degree

        for col in temperature_columns:
            coeffs = self.calibrate_polynomial(data[col], data["MeanTemperature"], degree)
            calibrated_temps[col] = np.polyval(coeffs, data[col])
            data[col] = calibrated_temps[col]
            print(f"For {col}: Coefficients = {coeffs}")

        # Set the timestamp as the index (converting from milliseconds to seconds)
        # data['TIMESTAMP'] = pd.to_datetime(data['TIMESTAMP'], unit='ms')
        # data.set_index('TIMESTAMP', inplace=True)

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
        # ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5, maxticks=20))
        # ax.xaxis.set_major_formatter(mdates.DateFormatter('%M:%S'))

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
        plt.savefig('target/' + plot_name + '.png')
        plt.show()

        pass
