import os
import heartpy as hp
import seaborn as snsc
import matplotlib.pyplot as plt
import pandas as pd
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

        self.plot_statistics()
        self.plot_statistics(['p01', 'p04', 'p05'])

    def get_statistics_for_phase(self, phase_start, phase_end):
        for hrv_data in self.all_hrv_data:
            sdnn, rmssd, lf_hf = hrv_data.get_statistics(phase_start, phase_end)
            self.sdnn_list.append(sdnn)
            self.rmssd_list.append(rmssd)
            self.lf_hf_list.append(lf_hf)

        print(
            f"{'start_sitting'} to {'stress_end'}: SDNN: {np.mean(self.sdnn_list)}, RMSSD: {np.mean(self.rmssd_list)}, LF/HF: {np.mean(self.lf_hf_list)}")

        self.sdnn_list = []
        self.rmssd_list = []
        self.lf_hf_list = []

    def get_statistics(self, phase_start, phase_end, probands):
        sdnn_list = []
        rmssd_list = []
        lf_hf_list = []
        pns_index_list = []
        sns_index_list = []
        stress_index_list = []

        for hrv_data in self.all_hrv_data:
            if hrv_data.proband not in probands:
                continue
            sdnn, rmssd, lf_hf = hrv_data.get_statistics(phase_start, phase_end)
            sdnn_list.append(sdnn)
            rmssd_list.append(rmssd)
            lf_hf_list.append(lf_hf)

        phase = ''
        if phase_start == 'start_sitting':
            phase = 'sitting'
        else:
            phase = 'stress'

        for kubios_data in self.all_hrv_data[0].kubios_data.values():
            pns_index_list.append(kubios_data[phase]['PNS_Index'])
            sns_index_list.append(kubios_data[phase]['SNS_Index'])
            stress_index_list.append(kubios_data[phase]['Stress_Index'])
            # 'PNS_Index': -1.6,
            # 'SD1_in_percent': 23,
            # 'Mean_RR': 673,
            # 'SNS_Index': 1.31,
            # 'SD2_in_percent': 77,
            # 'Stress_Index': 7,
            # 'Mean_HR': 89


        return sdnn_list, rmssd_list, lf_hf_list, pns_index_list, sns_index_list, stress_index_list

    def plot_statistics(self, probands=['p01', 'p02', 'p03','p04', 'p05']):
        (sitting_sdnn_list,
         sitting_rmssd_list,
         sitting_lf_hf_list,
         sitting_pns_index_list,
         sitting_sns_index_list,
         sitting_stress_index_list) = self.get_statistics('start_sitting', 'stroop_start', probands)  # Sitting phase
        (stress_sdnn_list,
         stress_rmssd_list,
         stress_lf_hf_list,
         stress_pns_index_list,
         stress_sns_index_list,
         stress_stress_index_list) = self.get_statistics('stroop_start', 'stress_end', probands)

        df_list_extended = []
        for phase, sdnn, rmssd, lf_hf, pns, sns, stress in zip(
                ['Baseline'] * len(sitting_sdnn_list) + ['Stress-Induced'] * len(stress_sdnn_list),
                sitting_sdnn_list + stress_sdnn_list,
                sitting_rmssd_list + stress_rmssd_list,
                sitting_lf_hf_list + stress_lf_hf_list,
                sitting_pns_index_list + stress_pns_index_list,
                sitting_sns_index_list + stress_sns_index_list,
                sitting_stress_index_list + stress_stress_index_list):
            df_list_extended.append({
                'Phase': phase,
                'SDNN': sdnn,
                'RMSSD': rmssd,
                'LF_HF': lf_hf,
                'PNS_Index': pns,
                'SNS_Index': sns,
                'Stress_Index': stress
            })

        df_extended = pd.DataFrame(df_list_extended)

        # Create boxplots
        fig, axes = plt.subplots(1, 6, figsize=(15, 3))
        if probands == ['p01', 'p04', 'p05']:
            fig.suptitle('HRV Metrics Comparison: Baseline vs Stress-Induced (Probands 1, 4, and 5)', fontsize=16)
        else:
            fig.suptitle('HRV Metrics Comparison: Baseline vs Stress-Induced (All Probands)', fontsize=16)

        # First row: SDNN, RMSSD, LF_HF
        snsc.boxplot(data=df_extended, x='Phase', y='SDNN', ax=axes[0])
        axes[0].set_title('SDNN', fontsize=14)
        axes[0].set_xlabel('')
        axes[0].set_ylabel('SDNN (in ms)', fontsize=14)

        snsc.boxplot(data=df_extended, x='Phase', y='RMSSD', ax=axes[1])
        axes[1].set_title('RMSSD', fontsize=14)
        axes[1].set_xlabel('')
        axes[1].set_ylabel('RMSSD (in ms)', fontsize=14)

        snsc.boxplot(data=df_extended, x='Phase', y='LF_HF', ax=axes[2])
        axes[2].set_title('LF/HF', fontsize=14)
        axes[2].set_xlabel('')
        axes[2].set_ylabel('LF/HF Ratio', fontsize=14)

        # Second row: PNS_Index, SNS_Index, Stress_Index
        snsc.boxplot(data=df_extended, x='Phase', y='PNS_Index', ax=axes[3])
        axes[3].set_title('PNS Index', fontsize=14)
        axes[3].set_xlabel('')
        axes[3].set_ylabel('PNS Index', fontsize=14)

        snsc.boxplot(data=df_extended, x='Phase', y='SNS_Index', ax=axes[4])
        axes[4].set_title('SNS Index', fontsize=14)
        axes[4].set_xlabel('')
        axes[4].set_ylabel('SNS Index', fontsize=14)

        snsc.boxplot(data=df_extended, x='Phase', y='Stress_Index', ax=axes[5])
        axes[5].set_title('Stress Index', fontsize=14)
        axes[5].set_xlabel('')
        axes[5].set_ylabel('Stress Index', fontsize=14)

        # Save the plot
        target_folder = "target"  # Replace with your actual folder path
        fig.tight_layout()
        if probands == ['p01', 'p04', 'p05']:
            fig.savefig(f"{target_folder}/hrv_metrics_comparison_145.png")
        else:
            fig.savefig(f"{target_folder}/hrv_metrics_comparison.png")

        plt.show()