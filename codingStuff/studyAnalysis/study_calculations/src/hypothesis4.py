import matplotlib.pyplot as plt
import numpy as np
import os


class Hypothesis4Analyzer:
    def __init__(self, all_calib_data, all_imu_data):
        self.all_calib_data = all_calib_data
        self.all_imu_data = all_imu_data
        self.target_folder = 'target'

    def analyze(self):
        for i, (calib_data, imu_data) in enumerate(zip(self.all_calib_data, self.all_imu_data)):
            self.plot_activity_and_temperature(calib_data, imu_data, i)

    def plot_activity_and_temperature(self, calib_data, imu_data, index):
        # Calculate activity level
        imu_data['activity_level'] = np.sqrt(imu_data['ACC_X'] ** 2 + imu_data['ACC_Y'] ** 2 + imu_data['ACC_Z'] ** 2)

        # Convert timestamps from milliseconds to minutes
        imu_data['TIMESTAMP'] = imu_data['TIMESTAMP'] / (1000 * 60)
        calib_data.raw_data['TIMESTAMP'] = calib_data.raw_data['TIMESTAMP'] / (1000 * 60)

        # Resample imu_data to match the timestamps in calib_data
        imu_data_resampled = imu_data.set_index('TIMESTAMP').reindex(calib_data.raw_data['TIMESTAMP']).reset_index()

        # Extract relevant data
        timestamps = calib_data.raw_data['TIMESTAMP']
        activity_levels = imu_data_resampled['activity_level']
        temperature = calib_data.raw_data['TympanicMembrane']  # replace with the actual column name for temperature

        # Create the plot
        fig, ax1 = plt.subplots()

        # Plotting temperature
        ax1.plot(timestamps, temperature, 'b-')
        ax1.set_xlabel('Time (minutes)')
        ax1.set_ylabel('Temperature (°C)', color='b')
        ax1.tick_params('y', colors='b')

        # Creating a second y-axis for activity level
        ax2 = ax1.twinx()
        ax2.fill_between(timestamps, activity_levels, color='g', alpha=0.3)
        ax2.set_ylabel('Activity Level', color='g')
        ax2.tick_params('y', colors='g')

        # Save the plot to the target folder
        plt.savefig(os.path.join(self.target_folder, f'h4_activity_and_temperature_plot_{index}.png'))

        plt.close(fig)
