import os

from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


class Hypothesis1Analyzer:
    def __init__(self, all_calib_data):
        self.all_calib_data = all_calib_data

    def boxplot(self):
        # Initialize an empty DataFrame to hold delta temperatures for all sensors
        delta_temp_df = pd.DataFrame(columns=['Sensor', 'Delta Temperature', 'ID'])

        # Iterate through all calibration data objects
        for calib_data in self.all_calib_data:
            real_temp_ground_truth = calib_data.real_temp_ground_truth

            for sensor in calib_data.temp_columns:
                # Calculate delta temperature
                delta_temp = calib_data.raw_data[sensor] - real_temp_ground_truth

                # Create a temporary DataFrame
                temp_df = pd.DataFrame({
                    'Sensor': [sensor] * len(delta_temp),
                    'Delta Temperature': delta_temp,
                    'ID': calib_data.raw_data['ID']  # Assuming 'ID' is in raw_data
                })

                # Append to the main DataFrame
                delta_temp_df = pd.concat([delta_temp_df, temp_df])

        # Create boxplots for each phase
        unique_phases = delta_temp_df['ID'].unique()
        for phase in unique_phases:
            phase_data = delta_temp_df[delta_temp_df['ID'] == phase]

            plt.figure(figsize=(12, 6))
            plt.title(f"Delta Temperature for Different Sensors (Phase {phase})")
            plt.xlabel("Sensor")
            plt.ylabel("Delta Temperature (°C)")

            plt.boxplot([phase_data[phase_data['Sensor'] == sensor]['Delta Temperature'] for sensor in
                         phase_data['Sensor'].unique()],
                        labels=phase_data['Sensor'].unique())

            plt.savefig(os.path.join("target/", f"hypothesis1_boxplot_phase_{phase}.png"), dpi=300)
            plt.close()

    def analyze_mean_error(self):
        # Initialize lists to store mean temperatures and errors for each location
        behind_ear_means = []
        in_ear_means = []
        behind_ear_errors = []
        in_ear_errors = []

        for calib_data in self.all_calib_data:
            # Filter data for phases 2 and 3 and 4
            phase_data = calib_data.raw_data[calib_data.raw_data['ID'].isin([2, 3, 4])]

            # Columns for behind the ear and in the ear
            behind_ear_columns = ['Out_Bottom', 'Out_Top', 'Out_Middle']
            in_ear_columns = ['TympanicMembrane', 'Concha', 'EarCanal']

            # Calculate mean temperature for each location
            mean_behind_ear = phase_data[behind_ear_columns].mean().mean()
            mean_in_ear = phase_data[in_ear_columns].mean().mean()

            # Calculate error based on ground truth (real_temp_ground_truth attribute in calib_data)
            ground_truth = calib_data.real_temp_ground_truth
            error_behind_ear = abs(mean_behind_ear - ground_truth)
            error_in_ear = abs(mean_in_ear - ground_truth)

            # Append to lists
            behind_ear_means.append(mean_behind_ear)
            in_ear_means.append(mean_in_ear)
            behind_ear_errors.append(error_behind_ear)
            in_ear_errors.append(error_in_ear)

        # Convert lists to NumPy arrays for statistical testing
        behind_ear_means = np.array(behind_ear_means)
        in_ear_means = np.array(in_ear_means)
        behind_ear_errors = np.array(behind_ear_errors)
        in_ear_errors = np.array(in_ear_errors)

        # Perform t-tests to compare means
        t_stat_means, p_val_means = stats.ttest_ind(behind_ear_means, in_ear_means)

        # Perform t-tests to compare errors
        t_stat_errors, p_val_errors = stats.ttest_ind(behind_ear_errors, in_ear_errors)

        print(f"Mean temperature behind the ear: {np.mean(behind_ear_means):.2f}")
        print(f"Mean temperature in the ear: {np.mean(in_ear_means):.2f}")
        print(f"T-test p-value for comparing means: {p_val_means}")

        print(f"Mean error behind the ear: {np.mean(behind_ear_errors):.2f}")
        print(f"Mean error in the ear: {np.mean(in_ear_errors):.2f}")
        print(f"T-test p-value for comparing errors: {p_val_errors}")
