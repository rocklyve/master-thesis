# for Hypothesis 3, you can use Pearson's correlation coefficient to test
# the relationship between relative changes in temperature readings from
# different sensor locations.
import os
import numpy as np
from scipy.stats import pearsonr, spearmanr
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from scipy import stats


class Hypothesis3Analyzer:
    def __init__(self, all_temp_data):
        self.avg_correlations = {}
        self.all_temp_data = all_temp_data

    # absolute abweichung anschauen

    def generate_heatmap(self):
        # Creating a DataFrame from the average correlations dictionary
        sensor_name_map = {
            'TympanicMembrane': 'Tympanic Membrane',
            'Concha': 'Concha',
            'EarCanal': 'Ear Canal',
            'Out_Bottom': 'Outer Ear Bottom',
            'Out_Top': 'Outer Ear Top',
            'Out_Middle': 'Outer Ear Middle'
        }

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

            # Rename the sensors
            heatmap_df.rename(index=sensor_name_map, columns=sensor_name_map, inplace=True)

            plt.figure(figsize=(10, 8))
            ax = sns.heatmap(heatmap_df, annot=True, fmt=".2f", cmap="coolwarm", center=0)
            ax.set(xlabel='')
            plt.title(f"Correlation Heatmap for Phase {phase}")
            plt.xlabel("")
            plt.ylabel("")

            # Save the plot
            plot_filename = os.path.join("target", f"Correlation_Heatmap_Phase_{phase}.png")
            plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
            plt.close()

    def analyze(self):
        self.avg_correlations = {}

        for temp_data in self.all_temp_data:
            for phase_id in [2, 3]:  # Phase 2 (Indoor), Phase 3 (Outdoor)
                phase_data = temp_data.raw_data[temp_data.raw_data['ID'] == phase_id]

                # Group every 6 rows and aggregate
                grouped_data = phase_data.groupby(phase_data.index // 6)
                aggregated_data = grouped_data.agg({
                    'TIMESTAMP': 'mean',
                    'ID': 'first',
                    **{col: 'first' for col in temp_data.temp_columns}
                }).dropna()

                # Calculate correlations for this participant and phase
                for sensor1 in temp_data.temp_columns:
                    for sensor2 in temp_data.temp_columns:
                        if sensor1 >= sensor2:
                            continue
                        corr, _ = spearmanr(aggregated_data[sensor1], aggregated_data[sensor2])

                        key = f"{sensor1}-{sensor2}-Phase{phase_id}"
                        if key not in self.avg_correlations:
                            self.avg_correlations[key] = []
                        self.avg_correlations[key].append(corr)

        # Average the Fisher Z-values across all participants and convert back to correlation
        for key, values in self.avg_correlations.items():
            self.avg_correlations[key] = np.mean(values)

        print(f"Average correlations for Phases 2 and 3: {self.avg_correlations}")

    def analyze_mad(self):
        mad_by_sensor = {'Indoor': {}, 'Outdoor': {}}

        for temp_data in self.all_temp_data:
            for phase, phase_id in [('Indoor', 2), ('Outdoor', 3)]:
                phase_data = temp_data.raw_data[temp_data.raw_data['ID'] == phase_id]
                if phase_data.empty:
                    continue

                for sensor in temp_data.temp_columns:
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
