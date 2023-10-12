import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

class Hypothesis3Analyzer:
    def __init__(self, all_calib_data, all_hrv_data, target_dir):
        self.all_calib_data = all_calib_data
        self.all_hrv_data = all_hrv_data
        self.target_dir = target_dir

    def analyze(self):
        # Create the target directory if it doesn't exist
        os.makedirs(self.target_dir, exist_ok=True)

        # Initialize dictionaries to store correlations
        correlations = {}
        correlations_participant_4 = {}  # For Participant 4 specifically

        # Loop through each participant's calibrated temperature and HRV data
        for idx, (calib_data, hrv_data) in enumerate(zip(self.all_calib_data, self.all_hrv_data)):
            # Filter data for phase 3
            phase3_data = calib_data.raw_data[calib_data.raw_data['ID'] == 3]

            # Generate timestamps for HRV data, assuming it starts at the same time as the temperature data
            hrv_timestamps = np.cumsum(hrv_data.hrv_df['RRIntervals']) / 1000  # Convert from ms to s
            hrv_timestamps = phase3_data['TIMESTAMP'].iloc[0] + hrv_timestamps  # Align with temperature data

            # Resample temperature data to align with HRV data
            phase3_data_resampled = phase3_data.set_index('TIMESTAMP').reindex(hrv_timestamps, method='nearest')

            for sensor in calib_data.temp_columns:
                # Drop NaNs only for the current sensor
                valid_indices = ~np.isnan(phase3_data_resampled[sensor]).values
                valid_temp_data = phase3_data_resampled[sensor].dropna()
                valid_hrv_data = hrv_data.hrv_df['RRIntervals'][valid_indices[:len(hrv_data.hrv_df['RRIntervals'])]]

                if len(valid_temp_data) > 0:  # Check if data is non-empty
                    if len(valid_temp_data) > 1 and len(valid_hrv_data) > 1:  # Check if data has at least 2 values
                        r, _ = pearsonr(valid_hrv_data, valid_temp_data)
                    else:
                        r = np.nan  # set correlation to NaN if not enough data
                    correlations[sensor] = correlations.get(sensor, []) + [r]

                    # If the participant is #4
                    if idx == 3:
                        correlations_participant_4[sensor] = r

        # Calculate mean correlation for each sensor
        mean_correlations = {sensor: np.mean(r_values) for sensor, r_values in correlations.items()}
        print('Hypothesis3: Mean correlations for all participants:')
        print(mean_correlations)
        print('Hypothesis3: Correlations for Participant 4:')
        print(correlations_participant_4)

        # Create and save plots
        plt.figure(figsize=(10, 6))
        # plt.bar(mean_correlations.keys(), mean_correlations.values(), color='b', alpha=0.7, label='All Participants')
        plt.bar(correlations_participant_4.keys(), correlations_participant_4.values(), color='r', alpha=0.7, label='Participant 4')
        plt.xlabel('Sensor')
        plt.ylabel('Mean Pearson Correlation')
        plt.title('Correlation Between HRV and Ear Temperature')
        plt.legend()
        plt.savefig(os.path.join(self.target_dir, 'hypothesis3_correlation_plot.png'))
        plt.close()