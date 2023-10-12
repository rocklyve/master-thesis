import os
import heartpy as hp
import matplotlib.pyplot as plt
import numpy as np


class HRVPipeline:
    def __init__(self, all_hrv_data):
        self.all_hrv_data = all_hrv_data
        self.sdnn_list = []
        self.rmssd_list = []
        self.lf_hf_list = []

    def analyze(self):
        # For all 3 phases together
        self.get_statistics_for_phase('start_sitting', 'stress_end')

        # For each of the 3 dually
        self.get_statistics_for_phase('start_sitting', 'stroop_start')  # Sitting phase
        self.get_statistics_for_phase('stroop_start', 'stress_end')  # Stress phase

        # Within stress phase
        self.get_statistics_for_phase('stroop_start', 'n-back_start')  # Stroop test
        self.get_statistics_for_phase('n-back_start', 'math_start')  # N-back test
        self.get_statistics_for_phase('math_start', 'stress_end')  # Math test


    def get_statistics_for_phase(self, phase_start, phase_end):
        for hrv_data in self.all_hrv_data:
            sdnn, rmssd, lf_hf = hrv_data.get_statistics(phase_start, phase_end)
            self.sdnn_list.append(sdnn)
            self.rmssd_list.append(rmssd)
            self.lf_hf_list.append(lf_hf)

        print(f"{'start_sitting'} to {'stress_end'}: SDNN: {np.mean(self.sdnn_list)}, RMSSD: {np.mean(self.rmssd_list)}, LF/HF: {np.mean(self.lf_hf_list)}")
        self.sdnn_list = []
        self.rmssd_list = []
        self.lf_hf_list = []