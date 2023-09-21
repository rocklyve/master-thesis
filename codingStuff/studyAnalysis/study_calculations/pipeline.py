import os
import numpy as np
import pandas as pd

from study_calculations.src.TemperatureCalibration import TemperatureCalibration
from study_calculations.src.hypothesis1 import Hypothesis1Analyzer
from study_calculations.src.hypothesis2 import Hypothesis2Analyzer


class AnalysisPipeline:
    def __init__(self, data_dir, target_dir):
        self.data_dir = data_dir
        self.target_dir = target_dir
        self.hypothesis1_results_by_phase = {}
        self.hypothesis2_results_by_phase = {}
        self.aggregated_results_by_phase = {}
        self.hypothesis1_analyzer = None
        self.hypothesis2_analyzer = None
        self.calib = None

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

        self.calib = TemperatureCalibration(
            df,
            temp_columns,
            os.path.basename(file_path),
            os.path.dirname(file_path),
            os.path.dirname(target_path)
        )

        self.calib.smooth_data()
        self.calib.plot_raw_data()

        participant = os.path.splitext(os.path.basename(file_path))[0]
        self.hypothesis1_results_by_phase = self.calib.test_hypothesis1_by_phase()

        print("")
        print("Hypothese 1: Results by phase:")
        print(self.hypothesis1_results_by_phase)
        print("")
        self.hypothesis1_analyzer = Hypothesis1Analyzer(
            self.calib.raw_data,
            temp_columns,
            self.aggregated_results_by_phase
        )
        self.hypothesis1_analyzer.aggregate_results_across_participants(self.hypothesis1_results_by_phase)

        # Store the results keyed by the participant (file name without extension)
        participant = os.path.splitext(os.path.basename(file_path))[0]
        self.hypothesis2_analyzer = Hypothesis2Analyzer(
            self.calib.raw_data,
            temp_columns,
            self.hypothesis2_results_by_phase
        )
        self.hypothesis2_results_by_phase = self.hypothesis2_analyzer.test_hypothesis2_by_phase()
        print("")
        print("Hypothesis 2: Results by phase:")
        print(self.hypothesis2_results_by_phase)
        print("")
        self.hypothesis2_analyzer.hypothesis2_results_by_phase[participant] = self.hypothesis2_results_by_phase


if __name__ == '__main__':
    data_dir = 'data/study_data'
    target_dir = 'target'

    pipeline = AnalysisPipeline(data_dir, target_dir)
    pipeline.process_directory(data_dir, target_dir)

    # Aggregation for Hypothesis 1
    aggregated_results_by_phase_h1 = pipeline.hypothesis1_analyzer.aggregate_results_by_phase()
    print("")
    print("Hypothesis 1: Aggregated results by phase:")
    print(aggregated_results_by_phase_h1)
    print("")

    # Aggregation for Hypothesis 2
    aggregated_results_for_h2 = (pipeline.hypothesis2_analyzer.
                                 aggregate_results_for_hypothesis2(pipeline.hypothesis2_results_by_phase)
                                 )
    print("")
    print("Hypothesis 2: Aggregated results:")
    print(aggregated_results_for_h2)
    print("")