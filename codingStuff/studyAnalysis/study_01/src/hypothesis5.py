import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
from tqdm import tqdm


class Hypothesis5Analyzer:

    def __init__(self, all_calib_data, output_folder):
        self.all_calib_data = all_calib_data
        self.output_folder = output_folder
        self.temp_columns = ['TympanicMembrane', 'Concha', 'EarCanal', 'Out_Bottom', 'Out_Top', 'Out_Middle']
        self.imu_columns = ['ACC_X', 'ACC_Y', 'ACC_Z', 'GYRO_X', 'GYRO_Y', 'GYRO_Z', 'MAG_X', 'MAG_Y', 'MAG_Z']
        self.yAxisRange = [0, 2.5]

    def filter_phases(self, data):
        return data[data['ID'].isin([2, 3, 4])].copy()

    def adjust_time_to_minutes(self, data, time_column='TIMESTAMP'):
        min_time = data[time_column].min()
        data['AdjustedTime'] = (data[time_column] - min_time) / 60000  # Convert to minutes
        return data

    def calculate_mean_movement(self, data):
        return data[self.imu_columns].mean(axis=1)

    def plot_mean_movement(self, mean_movement, axes):
        sns.lineplot(x='AdjustedTime', y=0, data=mean_movement, ax=axes[-1])
        print(mean_movement.head())
        axes[-1].set_title('Mean Movement')
        axes[-1].set_xlabel('Time (minutes)')
        axes[-1].set_ylabel('Mean Movement')

    def aggregate_absolute_relative_change(self, all_subject_data, sensor):
        aggregated_data = pd.concat(all_subject_data, axis=1)
        mean_data = aggregated_data.mean(axis=1).reset_index()
        mean_data['Sensor'] = sensor
        return mean_data

    def analyze(self):
        fig, axes = plt.subplots(7, 1, figsize=(8.27, 11.69))  # A4 size
        all_aggregated_imu_data = []
        aggregated_sensor_data = {sensor: [] for sensor in self.temp_columns}

        for calib in self.all_calib_data:
            phase_data = self.filter_phases(calib.raw_data)
            phase_data = self.adjust_time_to_minutes(phase_data)

            imu_data = self.calculate_mean_movement(phase_data)
            all_aggregated_imu_data.append(imu_data)

            for sensor in self.temp_columns:
                temp_data = phase_data[['AdjustedTime', sensor]].dropna()
                initial_value = temp_data[sensor].iloc[0]
                temp_data['AbsoluteRelativeChange'] = np.abs(temp_data[sensor] - initial_value)
                aggregated_sensor_data[sensor].append(temp_data['AbsoluteRelativeChange'])

        # Plot aggregated sensor data
        for i, (sensor, all_subject_data) in enumerate(aggregated_sensor_data.items()):
            mean_data = self.aggregate_absolute_relative_change(all_subject_data, sensor)
            sns.lineplot(x='index', y=0, data=mean_data, ax=axes[i])
            axes[i].set_title(f"{sensor} Mean Absolute Relative Change (MAR)")
            axes[i].set_xlabel('')
            axes[i].set_ylabel('MARC (°C)')
            axes[i].set_ylim(0, 5)

        # Plot mean movement
        mean_movement = pd.concat(all_aggregated_imu_data, axis=1).mean(axis=1).reset_index()
        mean_movement['AdjustedTime'] = self.adjust_time_to_minutes(mean_movement, 'index')[
            'AdjustedTime']  # Convert to minutes
        self.plot_mean_movement(mean_movement, axes)

        plt.tight_layout()
        plt.savefig(f"{self.output_folder}/Hypothesis5_Analysis.png", dpi=750)
