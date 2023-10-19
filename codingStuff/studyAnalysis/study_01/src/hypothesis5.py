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
        data['AdjustedTime'] = (data[time_column] - min_time)  # Convert to minutes
        return data

    def calculate_mean_movement(self, data):
        return data[self.imu_columns].mean(axis=1)

    def plot_mean_movement(self, mean_movement, axes):
        sns.lineplot(x='AdjustedTime', y=0, data=mean_movement, ax=axes[-1], color='black')
        min_time = mean_movement['AdjustedTime'].min()
        max_time = mean_movement['AdjustedTime'].max()
        axes[-1].set_xlim(min_time, max_time)
        axes[-1].xaxis.set_ticks(np.arange(min_time, max_time, 5))
        axes[-1].set_title('Mean Movement')
        axes[-1].set_xlabel('Time (minutes)')
        axes[-1].set_ylabel('Mean Movement')

    def aggregate_absolute_relative_change(self, all_subject_data, sensor):
        # Concatenate all subject data into a single DataFrame
        aggregated_data = pd.concat(all_subject_data)

        # Group by 'AdjustedTime' and calculate the mean of 'AbsoluteRelativeChange'
        mean_data = aggregated_data.groupby('AdjustedTime')['AbsoluteRelativeChange'].mean().reset_index()

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
                # initial_value = temp_data[sensor].iloc[0]
                temp_data['AbsoluteRelativeChange'] = temp_data[sensor].diff().abs().rolling(window=250).mean()
                aggregated_sensor_data[sensor].append(temp_data[['AdjustedTime', 'AbsoluteRelativeChange']])

        # Plot aggregated sensor data
        for i, (sensor, all_subject_data) in enumerate(aggregated_sensor_data.items()):
            mean_data = self.aggregate_absolute_relative_change(all_subject_data, sensor)
            custom_colors = ["#0064AE", "#FF801A", "#009800", "#D51C1E", "#8950E8", "#874A3D"]
            sns.lineplot(x='AdjustedTime', y='AbsoluteRelativeChange', data=mean_data, ax=axes[i],
                         color=custom_colors[i], errorbar=None)
            new_labels = [
                'Tympanic Membrane',
                'Concha',
                'Ear Canal',
                'Outer Ear Bottom',
                'Outer Ear Top',
                'Outer Ear Middle'
            ]
            min_time = mean_data['AdjustedTime'].min()
            max_time = mean_data['AdjustedTime'].max()
            axes[i].set_xlim(min_time, max_time)
            axes[i].xaxis.set_ticks(np.arange(min_time, max_time, 5))
            axes[i].set_title(f"{new_labels[i]} Mean Absolute Relative Change (MARC)")
            axes[i].set_xlabel('')
            axes[i].set_ylabel('MARC (°C)')
            axes[i].set_ylim(0, 0.09)

        # Plot mean movement
        mean_movement = pd.concat(all_aggregated_imu_data, axis=1).mean(axis=1).reset_index()
        mean_movement['AdjustedTime'] = self.adjust_time_to_minutes(mean_movement, 'index')[
            'AdjustedTime'] / 3000  # Convert to minutes
        # remove last 100 rows to make the plot look better
        mean_movement = mean_movement[:-5000].abs().rolling(window=25).mean()
        self.plot_mean_movement(mean_movement, axes)

        fig.suptitle('Mean Absolute Relative Change and Mean Movement Analysis', fontsize=16)

        plt.tight_layout()
        plt.savefig(f"{self.output_folder}/Hypothesis5_Analysis.png", dpi=750)
