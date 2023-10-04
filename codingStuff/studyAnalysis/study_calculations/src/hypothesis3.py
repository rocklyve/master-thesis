# for Hypothesis 3, you can use Pearson's correlation coefficient to test
# the relationship between relative changes in temperature readings from
# different sensor locations.
import os

import numpy as np
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


class Hypothesis3Analyzer:
    def __init__(self, all_calib_data):
        self.avg_correlations = {}
        self.all_calib_data = all_calib_data

    # absolute abweichung anschauen

    def generate_heatmap(self):
        # Creating a DataFrame from the average correlations dictionary
        df_list = []
        for k, v in self.avg_correlations.items():
            sensor1, sensor2, phase = k.split('-')
            df_list.append({
                'Sensor1': sensor1,
                'Sensor2': sensor2,
                'Phase': phase.replace('Phase', ''),
                'Correlation': v
            })
        df = pd.DataFrame(df_list)

        # Creating separate heatmaps for Phase 2 and Phase 3
        for phase in ['2', '3']:
            phase_df = df[df['Phase'] == phase]
            heatmap_df = phase_df.pivot(index="Sensor1", columns="Sensor2", values="Correlation")
            plt.figure(figsize=(10, 8))
            sns.heatmap(heatmap_df, annot=True, fmt=".2f", cmap="coolwarm", center=0)
            plt.title(f"Correlation Heatmap for Phase {phase}")

            # Save the plot in the target folder
            plot_filename = os.path.join("target", f"Correlation_Heatmap_Phase_{phase}.png")
            plt.savefig(plot_filename, dpi=300)
            plt.close()

    def analyze(self):
        correlations = {}
        for calib in self.all_calib_data:
            for phase in [2, 3]:  # Only consider Phases 2 and 3
                phase_data = calib.raw_data[calib.raw_data['ID'] == phase]
                if phase_data.empty:
                    continue
                for i, sensor1 in enumerate(calib.temp_columns):
                    for j, sensor2 in enumerate(calib.temp_columns):
                        if i >= j:
                            continue
                        key = f"{sensor1}-{sensor2}-Phase{phase}"
                        corr, _ = pearsonr(phase_data[sensor1], phase_data[sensor2])
                        if key in correlations:
                            correlations[key].append(corr)
                        else:
                            correlations[key] = [corr]

        # Calculate average correlations
        avg_correlations = {k: np.mean(v) for k, v in correlations.items()}
        print(f"Average correlations for Phases 2 and 3: {avg_correlations}")
        self.avg_correlations = avg_correlations

    def analyze_mad(self):
        mad_by_sensor = {'Indoor': {}, 'Outdoor': {}}

        for calib in self.all_calib_data:
            for phase, phase_id in [('Indoor', 2), ('Outdoor', 3)]:
                phase_data = calib.raw_data[calib.raw_data['ID'] == phase_id]
                if phase_data.empty:
                    continue

                for sensor in calib.temp_columns:
                    sensor_data = phase_data[sensor].dropna()  # Remove NaNs if any
                    mad_value = np.mean(np.absolute(sensor_data - np.mean(sensor_data)))  # Compute MAD

                    if sensor not in mad_by_sensor[phase]:
                        mad_by_sensor[phase][sensor] = []

                    mad_by_sensor[phase][sensor].append(mad_value)

        # Compute average MAD for each sensor and phase
        avg_mad_by_sensor = {}
        for phase in ['Indoor', 'Outdoor']:
            avg_mad_by_sensor[phase] = {}
            for sensor, values in mad_by_sensor[phase].items():
                avg_mad = np.mean(values)
                avg_mad_by_sensor[phase][sensor] = avg_mad

        print(f"Average MAD by sensor for Phases 2 (Indoor) and 3 (Outdoor): {avg_mad_by_sensor}")

    def calculate_relative_changes(self, readings):
        # Calculate relative changes for a single sensor
        # Assuming readings is a numpy array
        rel_changes = np.diff(readings) / readings[:-1] * 100  # In percentage
        return rel_changes
