import os
import heartpy as hp
import matplotlib.pyplot as plt
import numpy as np


class HRVPipeline:
    def __init__(self, folder_path, target_folder):
        self.folder_path = folder_path
        self.target_folder = target_folder

    def detect_stress(self, measures):
        # Example thresholds, these need to be calibrated based on individual or population data
        RMSSD_THRESHOLD = 50
        LFHF_THRESHOLD = 2.0

        rmssd = measures.get('RMSSD', 0)
        lf_hf_ratio = measures.get('LF/HF', 1)

        is_stressed = False

        if rmssd < RMSSD_THRESHOLD:
            print(f"Low RMSSD detected: {rmssd}")
            is_stressed = True

        if lf_hf_ratio > LFHF_THRESHOLD:
            print(f"High LF/HF ratio detected: {lf_hf_ratio}")
            is_stressed = True

        return is_stressed

    def process_files(self):
        txt_files = [f for f in os.listdir(self.folder_path) if f.endswith('.txt')]

        for txt_file in txt_files:
            print("Processing file:", txt_file)
            with open(os.path.join(self.folder_path, txt_file), 'r') as f:
                rr_intervals = np.array([int(line.strip()) for line in f])

            if rr_intervals.size == 0:
                print(f"Skipping empty file: {txt_file}")
                continue

            # Process RR-Intervals using heartpy
            try:
                working_data, measures = hp.process(rr_intervals, sample_rate=1000.0)
                plot_object = hp.plotter(working_data, measures, show=False)

                is_stressed = self.detect_stress(measures)
                if is_stressed:
                    print(f"Stress detected in {txt_file}")
                else:
                    print(f"No stress detected in {txt_file}")

                # Get the Axes object and modify x-ticks to show time in minutes
                ax = plot_object.gca()
                x_ticks = ax.get_xticks()
                ax.set_xticklabels(x_ticks * 10)  # Convert ms to minutes for the x-axis labels
                ax.set_xlabel('Time (min)')

                plot_object.savefig(os.path.join(self.target_folder, f"{os.path.splitext(txt_file)[0]}.png"))
            except Exception as e:
                print(f"Error processing {txt_file}: {e}")