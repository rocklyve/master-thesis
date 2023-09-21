import os
from scipy import stats
import numpy as np
from matplotlib import pyplot as plt


class TemperatureCalibration:

    def __init__(self, df, temp_columns, source_filename, data_folder, target_folder):
        self.raw_data = df
        self.temp_columns = temp_columns
        self.raw_data[temp_columns] = self.raw_data[temp_columns] / 100.0
        self.raw_data['TIMESTAMP'] = (self.raw_data['TIMESTAMP'] - self.raw_data['TIMESTAMP'].min()) / 1000.0 / 60.0
        self.mean_temp = self.raw_data[temp_columns].mean(axis=1)
        self.calibrated_data_dict = {}
        self.source_filename = source_filename
        self.data_folder = data_folder
        self.target_folder = target_folder  # New attribute to store the target folder

    def smooth_data(self):
        self.smoothed_data = self.raw_data.rolling(window=20).mean()

    def plot_raw_data(self):
        # Determine the suffix of the source filename
        source_filename_suffix = os.path.splitext(self.source_filename)[0]

        # Create the folder if it doesn't exist
        os.makedirs(self.data_folder, exist_ok=True)

        # Smoothing the raw data first
        self.smooth_data()
        smoothed_plot_data = self.smoothed_data[self.temp_columns]

        def add_background_color(ax):
            unique_ids = self.raw_data['ID'].unique()
            colors = plt.cm.jet(np.linspace(0, 1, len(unique_ids)))
            for i, unique_id in enumerate(unique_ids):
                id_data = self.raw_data[self.raw_data['ID'] == unique_id]
                ax.axvspan(id_data['TIMESTAMP'].min(), id_data['TIMESTAMP'].max(), facecolor=colors[i], alpha=0.2,
                           label=f'ID {unique_id}')

        # Create a plot for the smoothed raw data
        plt.figure(figsize=(8, 6), dpi=300)
        ax = plt.gca()
        plt.plot(self.raw_data['TIMESTAMP'], smoothed_plot_data)
        add_background_color(ax)
        plt.xlabel('Time (min)')
        plt.ylabel('Temperature (°C)')
        plt.title('Smoothed Raw Data')
        plt.legend(self.temp_columns, loc='lower right')
        plt.savefig(os.path.join(self.target_folder, f"{source_filename_suffix}_0smoothed_raw_data.png"), dpi=300)
        plt.close()


    # This method will:
    #
    # Calculate mean and standard deviation for temperatures behind the ear and for other locations (eardrum, ear canal, and auricle).
    # Perform t-tests to compare the means of the two groups.
    # Perform a one-way ANOVA to check for any statistically significant differences among the groups.
    def test_hypothesis1_by_phase(self):
        """
        Test the first hypothesis by phase:
        The temperature measured behind the ear is lower than that of the eardrum, ear canal, and auricle.

        Metrics:
        - Mean Temperature and Standard Deviation
        - t-test or ANOVA for significance
        """
        results_by_phase = {}

        # Get unique phase IDs
        unique_ids = self.raw_data['ID'].unique()

        for phase_id in unique_ids:
            phase_data = self.raw_data[self.raw_data['ID'] == phase_id]

            # Group temperature columns
            behind_ear_columns = ['Out_Bottom', 'Out_Top', 'Out_Middle']
            other_columns = ['TympanicMembrane', 'Concha', 'EarCanal']

            # Calculate mean and standard deviation
            mean_behind_ear = phase_data[behind_ear_columns].mean().mean()
            std_behind_ear = phase_data[behind_ear_columns].std().mean()

            mean_other = phase_data[other_columns].mean().mean()
            std_other = phase_data[other_columns].std().mean()

            # Conduct t-tests
            t_test_results = {}
            for col in other_columns:
                t_stat, p_val = stats.ttest_ind(phase_data[col], phase_data[behind_ear_columns].mean(axis=1))
                t_test_results[col] = (t_stat, p_val)

            # Conduct one-way ANOVA
            f_value, p_value_anova = stats.f_oneway(
                phase_data['TympanicMembrane'],
                phase_data['Concha'],
                phase_data['EarCanal'],
                phase_data[behind_ear_columns].mean(axis=1)
            )

            results_by_phase[phase_id] = {
                'mean_behind_ear': mean_behind_ear,
                'std_behind_ear': std_behind_ear,
                'mean_other': mean_other,
                'std_other': std_other,
                't_test_results': t_test_results,
                'anova_results': (f_value, p_value_anova)
            }

        return results_by_phase



