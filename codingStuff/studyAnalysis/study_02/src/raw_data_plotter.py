import matplotlib.pyplot as plt
import os

import pandas as pd
import seaborn as sns
import numpy as np


class RawDataPlotter:
    def __init__(self, all_temperature_data, all_hrv_data, source_dir, target_dir):
        self.all_temperature_data = all_temperature_data
        self.all_hrv_data = all_hrv_data
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.phase_timestamps = {}

    def plot_raw_data(self):
        self.get_phase_timestamps()
        os.makedirs(self.target_dir, exist_ok=True)
        participant_subfolders = [f.name for f in os.scandir(self.source_dir) if f.is_dir()]

        colors = ["#CCCCE5", "#CCE5FF", "#E5FFE4", "#FFE9C9", "#FFFFFF", "#FFFFFF"]

        for idx, (hrv_data, participant_subfolder) in enumerate(zip(self.all_hrv_data, participant_subfolders)):
            plt.figure(figsize=(10, 5), dpi=300)

            timestamps_seconds = np.cumsum(hrv_data.hrv_df['RRIntervals'])
            timestamps_minutes = timestamps_seconds / 1000 / 60.0

            smoothed_RRIntervals = pd.Series(hrv_data.hrv_df['RRIntervals']).rolling(window=50).mean()
            line, = plt.plot(timestamps_minutes, smoothed_RRIntervals, label='RR-Interval (ms)', linewidth=2)  # Label here

            proband = str(hrv_data.hrv_filepath.split('/')[1])
            phase_info = self.phase_timestamps.get(proband, {})

            for color, (phase, info) in zip(colors, phase_info.items()):
                min_timestamp = info['min_timestamp']
                duration = info['duration']
                plt.axvspan(min_timestamp, min_timestamp + duration, color=color, alpha=0.9)

            plt.xlim(timestamps_minutes.min(), timestamps_minutes.max())
            plt.title(f'Raw HRV Data of Subject {idx + 1}', fontsize=16)
            plt.xlabel('Time (min)', fontsize=14)
            plt.ylabel('RR-Interval (ms)', fontsize=14)

            plt.legend(handles=[line], loc='lower right')

            plot_path = os.path.join(self.target_dir, participant_subfolder, f'raw_hrv_data_participant_{idx + 1}.png')
            os.makedirs(os.path.dirname(plot_path), exist_ok=True)
            plt.tight_layout()
            plt.savefig(plot_path)
            plt.close()

    def get_phase_timestamps(self):
        for temp_data in self.all_temperature_data:
            # Get timestamps for each phase ('ID' column)
            proband = str(temp_data.source_filename.split('_')[2].split('.')[0])

            # Initialize sub-dictionary for each proband
            if proband not in self.phase_timestamps:
                self.phase_timestamps[proband] = {}

            for phase in temp_data.raw_data['ID'].unique():
                # Get first and last timestamp for each phase
                min_timestamp = temp_data.raw_data[temp_data.raw_data['ID'] == phase]['TIMESTAMP'].min()
                max_timestamp = temp_data.raw_data[temp_data.raw_data['ID'] == phase]['TIMESTAMP'].max()

                # Calculate duration
                duration = max_timestamp - min_timestamp

                # Save min_timestamp and duration for each phase
                self.phase_timestamps[proband][phase] = {'min_timestamp': min_timestamp, 'duration': duration}