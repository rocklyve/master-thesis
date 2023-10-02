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

        rmssd = measures.get('rmssd', 0)
        lf_hf_ratio = measures.get('LF/HF', 1)

        is_stressed = False

        if rmssd < RMSSD_THRESHOLD:
            print(f"Low RMSSD detected: {rmssd}")
            is_stressed = True

        if lf_hf_ratio > LFHF_THRESHOLD:
            print(f"High LF/HF ratio detected: {lf_hf_ratio}")
            is_stressed = True

        return is_stressed

    def plot_results(self, working_data, measures, label, target_folder, txt_file):
        plot_object = hp.plotter(working_data, measures, show=False)
        ax = plot_object.gca()
        x_ticks = ax.get_xticks()
        ax.set_xticklabels(x_ticks / 60000)  # Convert ms to minutes for the x-axis labels
        ax.set_xlabel('Time (min)')
        plot_object.suptitle(f"{label}")
        plot_object.savefig(os.path.join(target_folder, f"{os.path.splitext(txt_file)[0]}_{label}.png"))
        plt.close()

    def process_files(self):
        txt_files = [f for f in os.listdir(self.folder_path) if f.endswith('.txt')]

        for txt_file in txt_files:
            print("Processing file:", txt_file)
            with open(os.path.join(self.folder_path, txt_file), 'r') as f:
                rr_intervals = np.array([int(line.strip()) for line in f])

            if rr_intervals.size == 0:
                print(f"Skipping empty file: {txt_file}")
                continue

            sample_rate = 1000.0
            samples_15min = int(15 * 60)
            samples_13min = int(13 * 60)

            rr_15min = rr_intervals[:samples_15min]
            rr_13min = rr_intervals[samples_15min:samples_15min + samples_13min]
            rr_rest = rr_intervals[samples_15min + samples_13min:]

            for segment, label in zip([rr_15min, rr_13min, rr_rest], ['First 15 min', 'Next 13 min', 'Rest']):
                try:
                    working_data, measures = hp.process(segment, sample_rate)
                    print('rmssd: ', measures.get('rmssd', 0))
                    is_stressed = self.detect_stress(measures)
                    print(f"{label}: Stress detected" if is_stressed else f"{label}: No stress detected")

                    # Plot the results for this segment
                    self.plot_results(working_data, measures, label, self.target_folder, txt_file)

                except Exception as e:
                    print(f"Error processing {txt_file} for {label}: {e}")
