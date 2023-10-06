import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class Hypothesis6Analyzer:
    def __init__(self, all_calib_data):
        self.all_calib_data = all_calib_data

    def calculate_relative_change(self, series):
        return np.abs(series.pct_change() * 100)

    def analyze_all_participants(self, target_folder):
        # Initialize accumulators for each sensor and for movement
        sensor_data_accum = {sensor: [] for sensor in self.all_calib_data[0].temp_columns}
        movement_data_accum = []

        for calib in self.all_calib_data:
            for sensor in calib.temp_columns:
                sensor_data = calib.raw_data[sensor].dropna().reset_index(drop=True)
                rel_change = self.calculate_relative_change(sensor_data)
                sensor_data_accum[sensor].append(rel_change)

            imu_columns = ['ACC_X', 'ACC_Y', 'ACC_Z', 'GYRO_X', 'GYRO_Y', 'GYRO_Z', 'MAG_X', 'MAG_Y', 'MAG_Z']
            movement_data = np.sqrt((calib.raw_data[imu_columns] ** 2).sum(axis=1)).dropna().reset_index(drop=True)
            movement_data_accum.append(movement_data)

        # Take the average across all participants
        avg_sensor_data = {sensor: pd.concat(sensor_data_accum[sensor], axis=1).mean(axis=1).abs() for sensor in
                           sensor_data_accum}
        avg_movement_data = pd.concat(movement_data_accum, axis=1).mean(axis=1)

        # Plot the average data
        fig, axs = plt.subplots(len(avg_sensor_data) + 1, 1, figsize=(15, 20))

        for i, (sensor, data) in enumerate(avg_sensor_data.items()):
            axs[i].plot(data.index, data)
            axs[i].set_title(f"Average Rel Change {sensor}")
            axs[i].set_xlabel('Time (min)')
            axs[i].set_ylabel('Relative Change (%)')

        axs[-1].plot(avg_movement_data.index, avg_movement_data, alpha=0.3)
        axs[-1].set_title('Average Movement')
        axs[-1].set_xlabel('Time (min)')
        axs[-1].set_ylabel('Movement Magnitude')

        plt.tight_layout()
        plt.savefig(f"{target_folder}/hypothesis6_all_participants.png")
        plt.close()

    def analyze(self, target_folder):
        for i, calib in enumerate(self.all_calib_data):
            fig, axs = plt.subplots(len(calib.temp_columns) + 1, 1, figsize=(15, 20))

            # Loop over each sensor to plot its relative change
            for j, sensor in enumerate(calib.temp_columns):
                sensor_data = calib.raw_data[sensor].dropna().reset_index(drop=True)
                timestamps = calib.raw_data.loc[sensor_data.index, 'TIMESTAMP']
                rel_change = self.calculate_relative_change(sensor_data)
                axs[j].plot(timestamps, rel_change)
                axs[j].set_title(f"Rel Change {sensor}")
                axs[j].set_xlabel('Time (min)')
                axs[j].set_ylabel('Relative Change (%)')

                # Add vertical lines for phase changes
                phase_change_indices = calib.raw_data['ID'].diff().ne(0)
                phase_change_times = calib.raw_data.loc[phase_change_indices, 'TIMESTAMP']
                for phase_change_time in phase_change_times:
                    axs[j].axvline(x=phase_change_time, color='r', linestyle='--')

            # Plot the movement in the last subplot
            imu_columns = ['ACC_X', 'ACC_Y', 'ACC_Z', 'GYRO_X', 'GYRO_Y', 'GYRO_Z', 'MAG_X', 'MAG_Y', 'MAG_Z']
            movement_data = np.sqrt((calib.raw_data[imu_columns] ** 2).sum(axis=1)).dropna().reset_index(drop=True)
            axs[-1].plot(movement_data.index, movement_data, alpha=0.3)
            axs[-1].set_title('Movement')
            axs[-1].set_xlabel('Time (min)')
            axs[-1].set_ylabel('Movement Magnitude')

            # Save the figure
            plt.tight_layout()
            plt.savefig(f"{target_folder}/hypothesis6_participant_{i + 1}.png")
            plt.close()
