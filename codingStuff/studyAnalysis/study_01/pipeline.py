import os
import numpy as np
import pandas as pd
from study_01.src.TemperatureCalibration import TemperatureCalibration
from study_01.src.hypothesis1 import Hypothesis1Analyzer
from study_01.src.hypothesis2 import Hypothesis2Analyzer
from study_01.src.hypothesis3 import Hypothesis3Analyzer
from study_01.src.hypothesis4 import Hypothesis4Analyzer
from study_01.src.hypothesis5 import Hypothesis5Analyzer


class AnalysisPipeline:
    def __init__(self, data_dir, target_dir):
        self.data_dir = data_dir
        self.target_dir = target_dir
        self.all_calib_data = []
        self.all_imu_data = []
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

        # Replace 0 with NaN in temperature columns
        temp_columns = ['TympanicMembrane', 'Concha', 'EarCanal', 'Out_Bottom', 'Out_Top', 'Out_Middle']
        df[temp_columns] = df[temp_columns].replace(0, np.nan)

        # Extract proband number from file name
        basename = os.path.basename(file_path)
        proband_number = basename.split('_')[2].split('.')[0]

        # Look up real temperature ground truth based on proband number
        real_temp_ground_truth = self.ground_truth_temps.get(proband_number, 100.0)  # Default to 37.0 if not found

        calib = TemperatureCalibration(
            df,
            temp_columns,
            os.path.basename(file_path),
            os.path.dirname(file_path),
            os.path.dirname(target_path),
            real_temp_ground_truth
        )

        calib.smooth_data()
        # calib.plot_raw_data()
        self.all_calib_data.append(calib)



if __name__ == '__main__':
    # data_dir = 'data/study_data_test'
    data_dir = 'data/study_data'
    # data_dir = 'data/chess'
    target_dir = 'target'

    pipeline = AnalysisPipeline(data_dir, target_dir)
    pipeline.process_directory(data_dir, target_dir)

    # print("Analyzing hypothesis 1")
    # print('')
    # hypothesis1 = Hypothesis1Analyzer(pipeline.all_calib_data)
    # print("Mean and error of only sitting phase")
    # hypothesis1.analyze_mean_error([2])
    # print('')
    # print("Mean and error of phases 2,3,4")
    # hypothesis1.analyze_mean_error([2, 3, 4])
    # print('')
    # hypothesis1.boxplot()

    # print("Analyzing hypothesis 2")
    # hypothesis2 = Hypothesis2Analyzer(pipeline.all_calib_data)
    # hypothesis2.analyze()

    # print("Analyzing hypothesis 3")
    # hypothesis3 = Hypothesis3Analyzer(pipeline.all_calib_data)
    # hypothesis3.analyze()
    # hypothesis3.analyze_mad()
    # hypothesis3.generate_heatmap()
    #
    # print("Analyzing hypothesis 4")
    # hypothesis4 = Hypothesis4Analyzer(pipeline.all_calib_data)
    # hypothesis4.analyze()
    #
    print("Analyzing hypothesis 5")
    hypothesis5 = Hypothesis5Analyzer(pipeline.all_calib_data, target_dir)
    hypothesis5.analyze()
