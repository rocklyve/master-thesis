import numpy as np
import pandas as pd
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import seaborn as sns


class Hypothesis6Analyzer:
    def __init__(self, all_calib_data):
        self.all_calib_data = all_calib_data

    def calculate_magnitude(self, df, x, y, z):
        return np.sqrt(df[x] ** 2 + df[y] ** 2 + df[z] ** 2)

    def analyze(self, target_folder):
        aggregated_data = {'Indoor': [], 'Outdoor': []}

        for calib in self.all_calib_data:
            for phase, phase_id in [("Indoor", 2), ("Outdoor", 3)]:
                phase_data = calib.raw_data[calib.raw_data['ID'] == phase_id]

                if phase_data.empty:
                    continue

                acc_magnitude = self.calculate_magnitude(phase_data, 'ACC_X', 'ACC_Y', 'ACC_Z')

                for sensor in calib.temp_columns:
                    temp_data = phase_data[sensor].dropna()

                    common_indices = temp_data.index.intersection(acc_magnitude.index)

                    temp_data = temp_data.loc[common_indices]
                    acc_magnitude = acc_magnitude.loc[common_indices]

                    if len(common_indices) < 3:
                        continue

                    aggregated_data[phase].append((acc_magnitude, temp_data))

        for phase in ["Indoor", "Outdoor"]:
            avg_acc_magnitude = pd.concat([x[0] for x in aggregated_data[phase]]).groupby(level=0).mean()
            avg_temp_data = pd.concat([x[1] for x in aggregated_data[phase]]).groupby(level=0).mean()

            plt.figure(figsize=(10, 6))
            plt.scatter(avg_acc_magnitude, avg_temp_data)
            plt.title(f"Average Relationship between Movement (ACC_Magnitude) and Temperature during {phase}")
            plt.xlabel("ACC_Magnitude")
            plt.ylabel("Average Temperature")
            sns.regplot(x=avg_acc_magnitude, y=avg_temp_data, line_kws={"color": "red"})  # adding a best-fit line

            plt.savefig(f"{target_folder}/avg_scatter_{phase}.png")
            plt.close()
