import os

import numpy as np
from matplotlib import pyplot as plt
from scipy import stats


class Hypothesis1Analyzer:
    def __init__(self, all_calib_data, all_hrv_data, target_dir):
        self.all_calib_data = all_calib_data
        self.all_hrv_data = all_hrv_data
        self.target_dir = target_dir

    def analyze(self):
        # Create the target directory if it doesn't exist
        os.makedirs(self.target_dir, exist_ok=True)

        phase2_means = []
        phase3_means = []

        # Loop through each participant's calibrated temperature data
        for calib_data in self.all_calib_data:
            # Filter data by phase 2 and phase 3 using the 'ID' column
            phase2_data = calib_data.raw_data[calib_data.raw_data['ID'] == 2]
            phase3_data = calib_data.raw_data[calib_data.raw_data['ID'] == 3]

            # Compute the mean temperatures for each phase and sensor
            phase2_mean = phase2_data[calib_data.temp_columns].mean()
            phase3_mean = phase3_data[calib_data.temp_columns].mean()

            phase2_means.append(phase2_mean)
            phase3_means.append(phase3_mean)

        # Convert lists to NumPy arrays for easier manipulation
        phase2_means = np.array(phase2_means)
        phase3_means = np.array(phase3_means)

        # Compute the global mean across all sensors
        global_mean_phase2 = np.nanmean(phase2_means, axis=1)
        global_mean_phase3 = np.nanmean(phase3_means, axis=1)

        # Perform paired t-test for statistical significance
        t_stat, p_value = stats.ttest_rel(global_mean_phase2, global_mean_phase3)

        # Create and save the plot
        plt.figure(figsize=(10, 6))
        plt.bar(['Phase 2 (Relaxed)', 'Phase 3 (Stress)'],
                [np.nanmean(global_mean_phase2), np.nanmean(global_mean_phase3)],
                yerr=[np.nanstd(global_mean_phase2), np.nanstd(global_mean_phase3)], capsize=10)
        plt.title('Mean Ear Temperature During Relaxed and Stress Phases')
        plt.ylabel('Temperature (°C)')
        plt.xlabel('Phase')
        plt.text(0.5, max(np.nanmean(global_mean_phase2), np.nanmean(global_mean_phase3)),
                 f'p-value = {p_value:.4f}', horizontalalignment='center')
        plot_path = os.path.join(self.target_dir, 'hypothesis1_plot.png')
        plt.savefig(plot_path)
        plt.close()

        return t_stat, p_value
