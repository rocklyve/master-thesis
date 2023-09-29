import os
import numpy as np
import pandas as pd
from study_calculations.src.TemperatureCalibration import TemperatureCalibration
from study_calculations.src.hypothesis1 import Hypothesis1Analyzer
from study_calculations.src.hypothesis2 import Hypothesis2Analyzer
from study_calculations.src.hypothesis3 import Hypothesis3Analyzer


class AnalysisPipeline:
    def __init__(self, data_dir, target_dir):
        self.data_dir = data_dir
        self.target_dir = target_dir
        self.all_calib_data = []
        self.ground_truth_temps = {
            '01': 36.4,
            '02': 36.5,
            '03': 37.2,
            '04': 37.1,
            '05': 36.6,
            '06': 36.9,
            '07': 36.5,
            '08': 36.6,
            '09': 37.5,
            '10': 36.5,
            '11': 36.9,
            '12': 36.1,
            '13': 36.1,
            '14': 36.7,
        }

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

        # if first row temp_columns have a value equal to 0, then we have to remove the first 6 rows
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

        # Extract proband number from file name
        basename = os.path.basename(file_path)
        proband_number = basename.split('_')[2]  # Assumes the file name format is "Logging_person_x.csv"

        # Look up real temperature ground truth based on proband number
        real_temp_ground_truth = self.ground_truth_temps.get(proband_number, 37.0)  # Default to 37.0 if not found

        calib = TemperatureCalibration(
            df,
            temp_columns,
            os.path.basename(file_path),
            os.path.dirname(file_path),
            os.path.dirname(target_path),
            real_temp_ground_truth
        )

        calib.smooth_data()
        calib.plot_raw_data()
        self.all_calib_data.append(calib)


if __name__ == '__main__':
    # data_dir = 'data/study_data_test'
    data_dir = 'data/study_data'
    # data_dir = 'data/chess'
    target_dir = 'target'

    pipeline = AnalysisPipeline(data_dir, target_dir)
    pipeline.process_directory(data_dir, target_dir)

    hypothesis1 = Hypothesis1Analyzer(pipeline.all_calib_data)
    hypothesis1.analyze_mean_error()
    hypothesis1.boxplot()

    hypothesis2 = Hypothesis2Analyzer(pipeline.all_calib_data)
    hypothesis2.analyze()

    hypothesis3 = Hypothesis3Analyzer(pipeline.all_calib_data)
    hypothesis3.analyze()
