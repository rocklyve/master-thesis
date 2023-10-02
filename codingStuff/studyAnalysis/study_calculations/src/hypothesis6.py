import pandas as pd
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import seaborn as sns


class Hypothesis6Analyzer:
    def __init__(self, all_calib_data):
        self.all_calib_data = all_calib_data

    def analyze(self, target_folder):
        correlation_results = {}
        for calib in self.all_calib_data:
            for sensor1 in calib.temp_columns:
                for sensor2 in calib.temp_columns:
                    if sensor1 == sensor2:
                        continue
                    temp1 = calib.raw_data[sensor1].dropna()
                    temp2 = calib.raw_data[sensor2].dropna()

                    common_indices = temp1.index.intersection(temp2.index)
                    temp1 = temp1.loc[common_indices]
                    temp2 = temp2.loc[common_indices]

                    if len(common_indices) < 3:
                        continue

                    corr_coeff, p_value = pearsonr(temp1, temp2)
                    correlation_results[f"{sensor1}-{sensor2}"] = {
                        'correlation': corr_coeff,
                        'p_value': p_value
                    }

        # Convert to DataFrame
        corr_df = pd.DataFrame.from_dict(correlation_results, orient='index')

        self.generate_heatmap_hypothesis6(corr_df, target_folder)
        self.generate_correlation_table_hypothesis6(corr_df, target_folder)
        return correlation_results

    def generate_heatmap_hypothesis6(self, correlations, target_folder):
        corr_df = pd.DataFrame(correlations)
        plt.figure(figsize=(12, 9))
        sns.heatmap(corr_df, annot=True, cmap='coolwarm', fmt=".2f")
        plt.title('Heatmap of Pearson Correlations Between Sensor Positions')

        # Adding significance markers
        for y in range(corr_df.shape[0]):
            for x in range(corr_df.shape[1]):
                if corr_df.iloc[y, x] > 0.8:
                    plt.text(x + 0.5, y + 0.5, '*',
                             horizontalalignment='center',
                             verticalalignment='center',
                             fontsize=20, color='white')
        plt.savefig(f"{target_folder}/heatmap_hypothesis6.png")
        plt.close()

    def generate_correlation_table_hypothesis6(self, correlations, target_folder):
        corr_df = pd.DataFrame(correlations)
        fig, ax = plt.subplots(figsize=(12, 9))
        ax.axis('tight')
        ax.axis('off')
        table = ax.table(cellText=corr_df.values,
                         colLabels=corr_df.columns,
                         rowLabels=corr_df.index,
                         cellLoc='center', loc='center')

        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(2.0, 2.0)

        plt.savefig(f"{target_folder}/correlation_table_hypothesis6.png")
        plt.close()


