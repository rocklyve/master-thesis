import matplotlib.pyplot as plt
import os

import numpy as np


class RawDataPlotter:
    def __init__(self, all_calib_data, all_hrv_data, source_dir, target_dir):
        self.all_calib_data = all_calib_data
        self.all_hrv_data = all_hrv_data
        self.source_dir = source_dir
        self.target_dir = target_dir

    def plot_raw_data(self):
        # Create the target directory if it doesn't exist
        os.makedirs(self.target_dir, exist_ok=True)

        # Get participant subfolders
        participant_subfolders = [f.name for f in os.scandir(self.source_dir) if f.is_dir()]

        # Plotting HRV data
        for idx, (hrv_data, participant_subfolder) in enumerate(zip(self.all_hrv_data, participant_subfolders)):
            plt.figure(figsize=(12, 8))

            # Plot RR intervals. Assuming hrv_data is a NumPy array or list
            plt.plot(np.arange(len(hrv_data.hrv_df)), hrv_data.hrv_df)

            plt.title(f'Raw HRV Data for Participant {idx + 1}')
            plt.xlabel('Index')
            plt.ylabel('RR-Interval (ms)')

            plot_path = os.path.join(self.target_dir, participant_subfolder, f'raw_hrv_data_participant_{idx + 1}.png')
            os.makedirs(os.path.dirname(plot_path), exist_ok=True)
            plt.savefig(plot_path)
            plt.close()