import numpy as np
import pandas as pd
import heartpy as hp
from scipy.fft import fft


class HRVData:
    def __init__(self, hrv_df, hrv_timestamps, hrv_file_path, hrv_file_name):
        self.hrv_df = hrv_df
        self.proband = hrv_file_path.split('/')[1]
        self.hrv_timestamps = hrv_timestamps
        self.hrv_filepath = hrv_file_path
        self.hrv_filename = hrv_file_name
        self.kubios_data = {
            'p01': {
                'sitting': {
                    'PNS_Index': -1.6,
                    'SD1_in_percent': 23,
                    'Mean_RR': 673,
                    'SNS_Index': 1.31,
                    'SD2_in_percent': 77,
                    'Stress_Index': 7,
                    'Mean_HR': 89
                },
                'stress': {
                    'PNS_Index': -1.85,
                    'SD1_in_percent': 23,
                    'Mean_RR': 662,
                    'SNS_Index': 1.96,
                    'SD2_in_percent': 77,
                    'Stress_Index': 11,
                    'Mean_HR': 91
                },
                'relax': {
                    'PNS_Index': -0.99,
                    'SD1_in_percent': 28,
                    'Mean_RR': 696,
                    'SNS_Index': 0.82,
                    'SD2_in_percent': 72,
                    'Stress_Index': 6,
                    'Mean_HR': 86
                }
            },
            'p02': {
                'sitting': {
                    'PNS_Index': -0.92,
                    'SD1_in_percent': 30,
                    'Mean_RR': 729,
                    'SNS_Index': 0.87,
                    'SD2_in_percent': 70,
                    'Stress_Index': 8,
                    'Mean_HR': 82
                },
                'stress': {
                    'PNS_Index': -0.98,
                    'SD1_in_percent': 29,
                    'Mean_RR': 704,
                    'SNS_Index': 1.02,
                    'SD2_in_percent': 71,
                    'Stress_Index': 8,
                    'Mean_HR': 85
                },
                'relax': {
                    'PNS_Index': -0.56,
                    'SD1_in_percent': 32,
                    'Mean_RR': 785,
                    'SNS_Index': 0.5,
                    'SD2_in_percent': 68,
                    'Stress_Index': 8,
                    'Mean_HR': 76
                }
            },
            'p03': {
                'sitting': {
                    'PNS_Index': 2.21,
                    'SD1_in_percent': 45,
                    'Mean_RR': 1043,
                    'SNS_Index': -1.33,
                    'SD2_in_percent': 55,
                    'Stress_Index': 5,
                    'Mean_HR': 58
                },
                'stress': {
                    'PNS_Index': 0.92,
                    'SD1_in_percent': 37,
                    'Mean_RR': 896,
                    'SNS_Index': -0.51,
                    'SD2_in_percent': 63,
                    'Stress_Index': 6,
                    'Mean_HR': 63
                },
                'relax': {
                    'PNS_Index': 2.17,
                    'SD1_in_percent': 41,
                    'Mean_RR': 1042,
                    'SNS_Index': -1.25,
                    'SD2_in_percent': 59,
                    'Stress_Index': 5,
                    'Mean_HR': 58
                }
            },
            'p04': {
                'sitting': {
                    'PNS_Index': -0.51,
                    'SD1_in_percent': 35,
                    'Mean_RR': 844,
                    'SNS_Index': 0.33,
                    'SD2_in_percent': 65,
                    'Stress_Index': 9,
                    'Mean_HR': 65
                },
                'stress': {
                    'PNS_Index': -2.01,
                    'SD1_in_percent': 26,
                    'Mean_RR': 635,
                    'SNS_Index': 2.73,
                    'SD2_in_percent': 74,
                    'Stress_Index': 14,
                    'Mean_HR': 95
                },
                'relax': {
                    'PNS_Index': -0.66,
                    'SD1_in_percent': 32,
                    'Mean_RR': 856,
                    'SNS_Index': 0.54,
                    'SD2_in_percent': 68,
                    'Stress_Index': 11,
                    'Mean_HR': 70
                }
            },
            'p05': {
                'sitting': {
                    'PNS_Index': 7.26,
                    'SD1_in_percent': 52,
                    'Mean_RR': 1149,
                    'SNS_Index': -2.28,
                    'SD2_in_percent': 48,
                    'Stress_Index': 2,
                    'Mean_HR': 52
                },
                'stress': {
                    'PNS_Index': 6.44,
                    'SD1_in_percent': 48,
                    'Mean_RR': 1171,
                    'SNS_Index': -2.24,
                    'SD2_in_percent': 52,
                    'Stress_Index': 2,
                    'Mean_HR': 51
                },
                'relax': {
                    'PNS_Index': 10.13,
                    'SD1_in_percent': 52,
                    'Mean_RR': 1218,
                    'SNS_Index': -2.53,
                    'SD2_in_percent': 48,
                    'Stress_Index': 1,
                    'Mean_HR': 49
                }
            }
        }

    def time_to_index(self, time_str):
        """Converts time in 'minutes:seconds' format to index"""
        mins, secs = map(int, time_str.split(':'))
        total_secs = mins * 60 + secs
        total_ms = total_secs * 1000  # Convert to milliseconds

        # Sum up RR-intervals until total_ms is reached or exceeded
        rr_intervals = self.hrv_df['RRIntervals'].values
        elapsed_ms = 0
        index = 0
        for i, rr in enumerate(rr_intervals):
            elapsed_ms += rr
            if elapsed_ms >= total_ms:
                index = i
                break
        return index

    def print_statistics(self):
        proband_number = self.hrv_filepath.split('/')[2]
        print('Proband number: ', proband_number)
        # For all 3 phases together
        sdnn, rmssd, lf_hf_ratio = self.get_statistics('start_sitting', 'stress_end')
        print(f"{'start_sitting'} to {'stress_end'}: SDNN: {sdnn}, RMSSD: {rmssd}, LF/HF: {lf_hf_ratio}")

        # For each of the 3 dually
        sdnn, rmssd, lf_hf_ratio = self.get_statistics('start_sitting', 'stroop_start')  # Sitting phase
        print(f"sitting: SDNN: {sdnn}, RMSSD: {rmssd}, LF/HF: {lf_hf_ratio}")
        sdnn, rmssd, lf_hf_ratio = self.get_statistics('stroop_start', 'stress_end')  # Stress phase
        print(f"stress: SDNN: {sdnn}, RMSSD: {rmssd}, LF/HF: {lf_hf_ratio}")

        # Within stress phase
        # sdnn, rmssd, lf_hf_ratio = self.get_statistics('stroop_start', 'n-back_start')  # Stroop test
        # print(f"{'stroop_start'} to {'back_start'}: SDNN: {sdnn}, RMSSD: {rmssd}, LF/HF: {lf_hf_ratio}")
        # sdnn, rmssd, lf_hf_ratio = self.get_statistics('n-back_start', 'math_start')  # N-back test
        # print(f"{'back_start'} to {'math_start'}: SDNN: {sdnn}, RMSSD: {rmssd}, LF/HF: {lf_hf_ratio}")
        # sdnn, rmssd, lf_hf_ratio = self.get_statistics('math_start', 'stress_end')  # Math test
        # print(f"{'math_start'} to {'stress_end'}: SDNN: {sdnn}, RMSSD: {rmssd}, LF/HF: {lf_hf_ratio}")

        print("------")
        print(f"Kubios data for porband {proband_number}:")
        print("------")
        print(self.kubios_data[proband_number])
        print("------")
        print("------")

    def get_statistics(self, phase_start, phase_end):
        start_idx = self.time_to_index(self.hrv_timestamps[phase_start])
        end_idx = self.time_to_index(self.hrv_timestamps[phase_end])

        if start_idx >= end_idx or start_idx < 0 or end_idx > len(self.hrv_df['RRIntervals']):
            print(f"Invalid indices for {phase_start} to {phase_end}")
            return

        rr_intervals = self.hrv_df['RRIntervals'].values[start_idx:end_idx]

        if len(rr_intervals) == 0:
            print(f"No RR intervals found for {phase_start} to {phase_end}")
            return

        # Time-domain features
        sdnn = np.std(rr_intervals)
        rmssd = np.sqrt(np.mean(np.square(np.diff(rr_intervals))))

        # Frequency-domain feature
        lf_hf_ratio = self.calculate_lf_hf(rr_intervals)  # Assuming you've implemented this function

        return sdnn, rmssd, lf_hf_ratio


    def calculate_lf_hf(self, rr_intervals):
        # Calculate FFT
        freq = np.fft.fftfreq(len(rr_intervals))
        fft_values = fft(rr_intervals)

        # Calculate power spectral density
        psd = np.abs(fft_values) ** 2

        # Get LF and HF band limits in terms of array indices
        lf_band = (freq >= 0.04) & (freq <= 0.15)
        hf_band = (freq >= 0.15) & (freq <= 0.4)

        # Calculate power in LF and HF bands
        lf_power = np.sum(psd[lf_band])
        hf_power = np.sum(psd[hf_band])

        # Calculate LF/HF ratio
        lf_hf_ratio = lf_power / hf_power

        return lf_hf_ratio