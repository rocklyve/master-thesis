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

    def analyze(self):
        fig, axes = plt.subplots(7, 1, figsize=(8.3, 11.7))  # DIN A4 size

        # For IMU data
        all_imu_data = []
        for calib in tqdm(self.all_calib_data, desc="Processing IMU data"):
            phase_data = calib.raw_data[calib.raw_data['ID'].isin([2, 3, 4])]
            min_time = phase_data[phase_data['ID'] == 2]['TIMESTAMP'].min()
            phase_data['TIMESTAMP'] -= min_time  # Subtract min_time from all TIMESTAMPs
            imu_data = phase_data[self.imu_columns].mean(axis=1)
            all_imu_data.append(imu_data)

        mean_movement = pd.concat(all_imu_data, axis=1).mean(axis=1).reset_index()
        sns.lineplot(x='index', y=0, data=mean_movement, ax=axes[-1])
        axes[-1].set_title('Mean Movement')
        axes[-1].set_xlabel('Time (Adjusted)')
        axes[-1].set_ylabel('Mean Movement')

        # For each temperature sensor
        for idx, sensor in enumerate(tqdm(self.temp_columns, desc="Processing Temperature Sensors")):
            all_sensor_data = []
            for calib in self.all_calib_data:
                phase_data = calib.raw_data[calib.raw_data['ID'].isin([2, 3, 4])]
                min_time = phase_data[phase_data['ID'] == 2]['TIMESTAMP'].min()
                phase_data['TIMESTAMP'] -= min_time  # Subtract min_time from all TIMESTAMPs
                sensor_data = phase_data[sensor].dropna().diff().abs()
                all_sensor_data.append(sensor_data.reset_index(drop=True))

            mean_sensor_data = pd.concat(all_sensor_data, axis=1).mean(axis=1).reset_index()
            mean_sensor_data.columns = ['index', 'Temperature Change']
            sns.lineplot(x=mean_sensor_data.columns[0], y=mean_sensor_data.columns[1], data=mean_sensor_data, ax=axes[idx])
            axes[idx].set_title(f'{sensor} Absolute Change')
            axes[idx].set_xlabel('Time (Adjusted)')
            axes[idx].set_ylabel('Temperature Change (°C)')

        plt.tight_layout()
        plt.savefig(f"{self.output_folder}/Hypothesis5_Analysis.pdf")
        plt.show()

    def analyze2(self):
        all_participant_data = {col: [] for col in self.temp_columns}
        all_participant_data['MeanMovement'] = []

        for calib_obj in self.all_calib_data:
            df = calib_obj.raw_data
            initial_timestamp = df['TIMESTAMP'].min()  # To correct the time range in the plot

            df_phase2 = df[df['ID'] == 2]
            df_phase2 = df_phase2[df_phase2['TIMESTAMP'] <= df_phase2['TIMESTAMP'].min() + 20 * 60 * 1000]

            df_phase3 = df[df['ID'] == 3]
            df_phase3 = df_phase3[df_phase3['TIMESTAMP'] <= df_phase3['TIMESTAMP'].min() + 20 * 60 * 1000]

            df_combined = pd.concat([df_phase2, df_phase3])

            with PdfPages(os.path.join(self.output_folder,
                                       f"{calib_obj.source_filename.split('.')[0]}_hypothesis5.pdf")) as pdf:
                fig, axes = plt.subplots(len(self.temp_columns) + 1, 1, figsize=(8.27, 11.69))  # DIN A4 size in inches

                for i, col in enumerate(self.temp_columns):
                    relative_change = self.plot_temp_sensor(df_combined, col, axes[i], initial_timestamp)
                    if relative_change is not None:
                        all_participant_data[col].append(relative_change)

                # Calculate mean IMU movement for this participant and plot it
                mean_movement = self.calculate_mean_movement(df_combined)
                if mean_movement is not None:
                    all_participant_data['MeanMovement'].append(mean_movement.values)

                axes[-1].plot((mean_movement.index - initial_timestamp) / (60 * 1000) * 18 - 18, mean_movement)
                axes[-1].set_title('Mean Movement')
                axes[-1].set_xlabel('Time (min)')
                axes[-1].set_ylabel('Mean Movement')

                plt.tight_layout()
                pdf.savefig(fig)

        # Filter out None values before finding min_length
        min_length = min(
            len(x) for col in self.temp_columns + ['MeanMovement'] for x in all_participant_data[col] if x is not None)

        # Filter out None values and trim or pad data series to the same length
        for col in self.temp_columns + ['MeanMovement']:
            all_participant_data[col] = [x[:min_length] for x in all_participant_data[col] if x is not None]

        # Generate overall plot for mean data across all participants
        with PdfPages(os.path.join(self.output_folder, "overall_mean_data_hypothesis5.pdf")) as pdf:
            fig, axes = plt.subplots(len(self.temp_columns) + 1, 1, figsize=(8.27, 11.69))  # DIN A4 size in inches

            for i, col in enumerate(self.temp_columns):
                if len(all_participant_data[col]) > 0 and not np.all(np.isnan(all_participant_data[col])):
                    overall_mean_data = np.nanmean(all_participant_data[col], axis=0)
                else:
                    # Handle the case where there's no valid data.
                    overall_mean_data = None
                # Multiply time value by 13.3333
                axes[i].plot(np.linspace(0, min_length / (60 * 1000) * 115, min_length), overall_mean_data * 10)
                axes[i].set_title(f"{col}: Overall Mean Relative Change")
                # axes[i].set_xlabel('Time (min)')
                axes[i].set_ylabel('Relative Change (%)')  # Percentage for relative change
                axes[i].set_ylim([0, 5])  # 0-100% for relative change

            overall_mean_movement = np.nanmean(all_participant_data['MeanMovement'], axis=0)
            axes[-1].plot(np.linspace(0, min_length / (60 * 1000) * 115, min_length), overall_mean_movement)
            axes[-1].set_title('Overall Mean Movement')
            axes[-1].set_xlabel('Time (min)')
            axes[-1].set_ylabel('Mean Movement')

            plt.tight_layout()
            pdf.savefig(fig)

    def plot_temp_sensor(self, df, sensor_name, ax, initial_timestamp):
        sensor_data = df[sensor_name].dropna()
        if sensor_data.empty:
            return None  # Skip if there is no data

        relative_change = self.calculate_relative_change(sensor_data).abs()
        ax.plot((sensor_data.index - initial_timestamp) / (60 * 1000) * 18 - 18,
                relative_change)  # Convert time to minutes and correct the timestamp
        ax.set_title(f"{sensor_name} Relative Change")
        # ax.set_xlabel('Time (min)')
        ax.set_ylabel('Relative Change (%)')  # Percentage for relative change
        ax.set_ylim(self.yAxisRange)  # 0-100% for relative change
        return relative_change.values  # Return the relative change values for later use

    def calculate_relative_change(self, series):
        return np.abs(series.pct_change() * 100)

    def calculate_mean_movement(self, df):
        # Use the user's method for calculating movement
        imu_data = df[self.imu_columns].dropna()
        if imu_data.empty:
            return None  # Skip if there is no data

        return np.sqrt((imu_data ** 2).sum(axis=1))
