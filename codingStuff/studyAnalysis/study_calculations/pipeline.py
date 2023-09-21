import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import ttest_ind_from_stats
from enum import Enum, auto

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

    def test_hypothesis2_by_phase(self):
        """
        Test the second hypothesis by phase:
        The fluctuations in temperature readings are less indoors than outdoors.

        Metrics:
        - Standard Deviation
        - t-test for significance of variance
        """
        results_by_phase = {}

        # Get unique phase IDs
        unique_ids = self.raw_data['ID'].unique()

        for phase_id in unique_ids:
            phase_data = self.raw_data[self.raw_data['ID'] == phase_id]
            std_all = phase_data[self.temp_columns].std().mean()

            # Condition (indoor or outdoor) based on phase ID
            condition = 'Indoor' if phase_id == 2 else 'Outdoor' if phase_id == 3 else 'Unknown'

            results_by_phase[phase_id] = {
                'std_all': std_all,
                'condition': condition
            }

        return results_by_phase


class AnalysisPipeline:

    def __init__(self, data_dir, target_dir):
        self.data_dir = data_dir
        self.target_dir = target_dir
        # self.aggregated_results = {}
        self.aggregated_results_by_phase = {}
        self.hypothesis2_results_by_phase = {}

    def process_directory(self, dir_path, target_path):
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            item_target_path = os.path.join(target_path, item)
            if os.path.isdir(item_path):
                os.makedirs(item_target_path, exist_ok=True)
                self.process_directory(item_path, item_target_path)
            elif item_path.endswith('.csv'):
                self.process_file(item_path, item_target_path)

    def process_file(self, file_path, target_path):
        print(f"Processing file: {file_path}")
        df = pd.read_csv(file_path)

        temp_columns = ['TympanicMembrane', 'Concha', 'EarCanal', 'Out_Bottom', 'Out_Top', 'Out_Middle']
        # if first row temp_colums have a value equal to 0, then we have to remove the first 6 rows
        if df[temp_columns].iloc[0].sum() <= 4000:
            # Make sure we only keep complete sets of 6 rows
            num_rows_to_keep = len(df) // 6 * 6
            df = df.iloc[:num_rows_to_keep]

            df['MEAN_TIMESTAMP'] = (df['TIMESTAMP'].groupby(df.index // 6).transform('mean') / 6).astype('int64')
            majority_ids = df['ID'].groupby(df.index // 6).transform(lambda x: x.value_counts().idxmax())

            df = df.groupby(df.index // 6).apply(lambda x: x.sum())

            # Calculate the mean TIMESTAMP and use the most frequent ID
            df['TIMESTAMP'] = df['MEAN_TIMESTAMP']
            # df['ID'] = np.around(df['MAJORITY_ID']).astype('int') / 6
            df['ID'] = majority_ids.groupby(majority_ids.index // 6).first()

            df.drop([
                'MEAN_TIMESTAMP',
                'ACC_X',
                'ACC_Y',
                'ACC_Z',
                'GYRO_X',
                'GYRO_Y',
                'GYRO_Z',
                'MAG_X',
                'MAG_Y',
                'MAG_Z'
            ], axis=1, inplace=True)

            # modified_file_path = os.path.splitext(file_path)[0] + "_modified.csv"
            # df.to_csv(modified_file_path, index=False)

        # this was used to remove the first minute and last 10 seconds rows
        # df = df.iloc[3000:]
        # df = df.iloc[:-500]

        calib = TemperatureCalibration(df, temp_columns, os.path.basename(file_path), os.path.dirname(file_path), os.path.dirname(target_path))
        calib.smooth_data()
        calib.plot_raw_data()

        participant = os.path.splitext(os.path.basename(file_path))[0]
        hypothesis1_results_by_phase = calib.test_hypothesis1_by_phase()

        print("")
        print("Hypothese 1: Results by phase:")
        print(hypothesis1_results_by_phase)
        print("")

        # call and print the results of hypothesis 2

        # Store the results keyed by the participant (file name without extension)
        # participant = os.path.splitext(os.path.basename(file_path))[0]
        # self.aggregated_results[participant] = hypothesis1_results_by_phase
        self.aggregate_results_across_participants(hypothesis1_results_by_phase)

        # Call and store the results of hypothesis 2
        hypothesis2_results_by_phase = calib.test_hypothesis2_by_phase()
        print("")
        print("Hypothesis 2: Results by phase:")
        print(hypothesis2_results_by_phase)
        print("")

        # Store the results keyed by the participant (file name without extension)
        participant = os.path.splitext(os.path.basename(file_path))[0]
        self.hypothesis2_results_by_phase[participant] = hypothesis2_results_by_phase

    # This function calculates the Mean Absolute Error between two lists
    def calculate_mae(self, list1, list2):
        return np.mean(np.abs(np.array(list1) - np.array(list2)))

    def aggregate_results_across_participants(self, hypothesis1_results_by_phase):
        """
        Aggregate results across all participants for hypothesis 1.
        This could include calculating global means, standard deviations, etc.
        """
        # Initialize aggregation variables
        for phase_id, stats in hypothesis1_results_by_phase.items():
            if phase_id not in self.aggregated_results_by_phase:
                self.aggregated_results_by_phase[phase_id] = {
                    'mean_behind_ear': [],
                    'std_behind_ear': [],
                    'mean_other': [],
                    'std_other': []
                }

            self.aggregated_results_by_phase[phase_id]['mean_behind_ear'].append(stats['mean_behind_ear'])
            self.aggregated_results_by_phase[phase_id]['std_behind_ear'].append(stats['std_behind_ear'])
            self.aggregated_results_by_phase[phase_id]['mean_other'].append(stats['mean_other'])
            self.aggregated_results_by_phase[phase_id]['std_other'].append(stats['std_other'])

    def aggregate_results_by_phase(self):
        """
        Aggregate results across all participants for hypothesis 1, by each phase.
        This includes calculating mean and standard deviations for each phase.
        """
        aggregated_results = {}

        for phase_id, stats in self.aggregated_results_by_phase.items():
            global_mean_behind_ear = np.mean(stats['mean_behind_ear'])
            global_mean_other = np.mean(stats['mean_other'])

            mae = self.calculate_mae(stats['mean_behind_ear'], stats['mean_other'])
            global_mae_behind_ear = np.mean(np.abs(np.array(stats['mean_behind_ear']) - global_mean_behind_ear))
            global_mae_other = np.mean(np.abs(np.array(stats['mean_other']) - global_mean_other))

            aggregated_results[phase_id] = {
                'global_mean_behind_ear': global_mean_behind_ear,
                'global_std_behind_ear': np.mean(stats['std_behind_ear']),
                'global_mean_other': global_mean_other,
                'global_std_other': np.mean(stats['std_other']),
                'global_mae': mae,
                'global_mae_behind_ear': global_mae_behind_ear,
                'global_mae_other': global_mae_other
            }
        return aggregated_results

    def aggregate_results_for_hypothesis2(self, results_by_phase):
        """
        Aggregate results across all participants for hypothesis 2.
        This includes calculating mean standard deviations for each condition (indoor and outdoor).
        """
        aggregated_results = {'Indoor': [], 'Outdoor': []}

        for participant, phase_results in results_by_phase.items():
            for phase_id, stats in phase_results.items():
                if stats['condition'] in ['Indoor', 'Outdoor']:
                    aggregated_results[stats['condition']].append(stats['std_all'])

        aggregated_stats = {
            'global_std_indoor': np.mean(aggregated_results['Indoor']),
            'global_std_outdoor': np.mean(aggregated_results['Outdoor'])
        }

        return aggregated_stats


if __name__ == '__main__':
    data_dir = 'data/study_data'
    target_dir = 'target'

    pipeline = AnalysisPipeline(data_dir, target_dir)
    pipeline.process_directory(data_dir, target_dir)

    # Aggregation for Hypothesis 1
    aggregated_results_by_phase_h1 = pipeline.aggregate_results_by_phase()
    print("")
    print("Hypothesis 1: Aggregated results by phase:")
    print(aggregated_results_by_phase_h1)
    print("")

    # Aggregation for Hypothesis 2
    aggregated_results_for_h2 = pipeline.aggregate_results_for_hypothesis2(pipeline.hypothesis2_results_by_phase)
    print("")
    print("Hypothesis 2: Aggregated results:")
    print(aggregated_results_for_h2)
    print("")