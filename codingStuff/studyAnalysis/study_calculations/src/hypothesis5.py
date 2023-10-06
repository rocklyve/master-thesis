import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class Hypothesis5Analyzer:
    def __init__(self, all_calib_data):
        self.all_calib_data = all_calib_data

    def calculate_relative_change(self, series):
        return np.abs(series.pct_change() * 100)

    def calculate_movement(self, df, imu_columns):
        return np.sqrt((df[imu_columns] ** 2).sum(axis=1))

    def analyze(self, target_folder):
        for i, calib in enumerate(self.all_calib_data):
            fig, axes = plt.subplots(7, 1, figsize=(8.27, 11.7), sharex=True)

            # Filter data for phase 2 and 3
            filtered_data = calib.raw_data[(calib.raw_data['ID'] == 2) | (calib.raw_data['ID'] == 3)]

            # Calculate relative change for each temperature sensor
            for j, sensor in enumerate(calib.temp_columns):
                sensor_data = filtered_data[sensor].dropna().reset_index(drop=True)
                rel_change = self.calculate_relative_change(sensor_data)
                axes[j].plot(rel_change, label=f"Rel Change {sensor}")
                axes[j].set_title(f"Rel Change {sensor}")

            # Calculate movement
            imu_columns = ['ACC_X', 'ACC_Y', 'ACC_Z', 'GYRO_X', 'GYRO_Y', 'GYRO_Z', 'MAG_X', 'MAG_Y', 'MAG_Z']
            movement = self.calculate_movement(filtered_data, imu_columns)
            axes[-1].plot(movement, label='Movement', alpha=0.3)
            axes[-1].set_title('Movement')

            plt.suptitle(f"Participant {i + 1}")
            plt.savefig(f"{target_folder}/hypothesis6_participant_{i + 1}.png")
            plt.close()

    def analyze_all_participants(self, target_folder):
        avg_rel_changes = {}
        avg_movement = None

        for calib in self.all_calib_data:
            # Filter data for Phase 2 and Phase 3 (ID == 2 or ID == 3)
            filtered_data = calib.raw_data[calib.raw_data['ID'].isin([2, 3])]

            # Calculate movement
            imu_columns = ['ACC_X', 'ACC_Y', 'ACC_Z', 'GYRO_X', 'GYRO_Y', 'GYRO_Z', 'MAG_X', 'MAG_Y', 'MAG_Z']
            movement_data = self.calculate_movement(filtered_data, imu_columns)

            # Sync movement and temperature data
            synced_data = self.sync_data(pd.DataFrame({'TIMESTAMP': filtered_data['TIMESTAMP'], 'Movement': movement_data}),
                                         filtered_data)

            # Calculate and accumulate the average relative change for each sensor
            for sensor in calib.temp_columns:
                rel_change = self.calculate_relative_change(synced_data[sensor].dropna())
                if sensor not in avg_rel_changes:
                    avg_rel_changes[sensor] = []
                avg_rel_changes[sensor].append(rel_change)

            # Calculate and accumulate the average movement
            if avg_movement is None:
                avg_movement = movement_data
            else:
                avg_movement += movement_data

        # Calculate the final averages
        for sensor in avg_rel_changes:
            avg_rel_changes[sensor] = pd.concat(avg_rel_changes[sensor], axis=1).mean(axis=1)
        avg_movement = avg_movement / len(self.all_calib_data)

        # Plotting
        fig, axs = plt.subplots(len(calib.temp_columns) + 1, 1, figsize=(8.27, 11.69))  # A4 size

        for i, (sensor, rel_change) in enumerate(avg_rel_changes.items()):
            axs[i].plot(rel_change.index, rel_change, label=f'Avg Rel Change {sensor}')
            axs[i].set_ylabel('Rel Change (%)')
            axs[i].legend()

        axs[-1].plot(avg_movement.index, avg_movement, label='Avg Movement', alpha=0.3)
        axs[-1].set_xlabel('Time (minutes)')
        axs[-1].set_ylabel('Movement')
        axs[-1].legend()

        plt.tight_layout()
        plt.savefig(f"{target_folder}/hypothesis6_all_participants.png")
        plt.close(fig)

    # Syncing the movement and temperature data based on their timestamps
    def sync_data(self, movement_data, temperature_data):
        # Assuming the TIMESTAMP column is in minutes in both dataframes
        synced_data = pd.merge_asof(temperature_data.sort_values('TIMESTAMP'),
                                    movement_data.sort_values('TIMESTAMP'),
                                    on='TIMESTAMP',
                                    direction='nearest')
        return synced_data