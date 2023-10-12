import os
import pandas as pd
from study_02.src.TemperatureCalibration import TemperatureCalibration
from study_02.src.hrv_data import HRVData
from study_02.src.hrv_pipeline import HRVPipeline
import numpy as np

from study_02.src.hypothesis1 import Hypothesis1Analyzer
from study_02.src.hypothesis2 import Hypothesis2Analyzer
from study_02.src.hypothesis3 import Hypothesis3Analyzer
from study_02.src.hypothesis4 import Hypothesis4Analyzer
from study_02.src.raw_data_plotter import RawDataPlotter


class Study2Pipeline:
    def __init__(self, data_dir, target_dir):
        self.data_dir = data_dir
        self.target_dir = target_dir
        self.all_calib_data = []
        self.all_hrv_data = []
        self.ground_truth_temperature = {
            'p01': 36.9,
            'p02': 37.2,
            'p03': 37.1,
            'p04': 37.1,
            'p05': 36.8,
        }
        self.hrv_timestamps = {
            'p01': {
                'start': '2023-10-02 16-22-36',
                'start_sitting': '22:00',
                'stroop_start': '37:00',
                'n-back_start': '39:40',
                'math_start': '46:22',
                'stress_end': '55:00',
            },
            'p02': {
                'start': '2023-10-03 10-11-30',
                'start_sitting': '21:00',
                'stroop_start': '36:06',
                'n-back_start': '38:43',
                'math_start': '40:23',
                'stress_end': '48:29',
            },
            'p03': {
                'start': '2023-10-04 09-12-28',
                'start_sitting': '21:20',
                'stroop_start': '36:40',
                'n-back_start': '39:10',
                'math_start': '42:35',
                'stress_end': '50:50',
            },
            'p04': {
                'start': '2023-10-04 13-30-48',
                'start_sitting': '22:00',
                'stroop_start': '37:00',
                'n-back_start': '39:30',
                'math_start': '45:12',
                'stress_end': '53:45',
            },
            'p05': {
                'start': '2023-10-04 15-08-32',
                'start_sitting': '21:00',
                'stroop_start': '35:52',
                'n-back_start': '38:30',
                'math_start': '43:55',
                'stress_end': '52:10',
            },
        }

    def process_directory(self):
        for participant_folder in os.listdir(self.data_dir):
            participant_path = os.path.join(self.data_dir, participant_folder)
            if os.path.isdir(participant_path):
                self.process_participant(participant_path)

    def process_participant(self, participant_path):
        temp_file = [f for f in os.listdir(participant_path) if f.endswith('.csv')][0]
        hrv_file = [f for f in os.listdir(participant_path) if f.endswith('.txt')][0]

        temp_file_path = os.path.join(participant_path, temp_file)
        hrv_file_path = os.path.join(participant_path, hrv_file)

        # Process temperature data
        temp_df = pd.read_csv(temp_file_path)
        temp_columns = ['TympanicMembrane', 'Concha', 'EarCanal', 'Out_Bottom', 'Out_Top', 'Out_Middle']
        temp_df[temp_columns] = temp_df[temp_columns].replace(0, np.nan)

        # Process HRV data
        timestamps = self.hrv_timestamps[os.path.basename(participant_path)]
        hrv_df = pd.read_csv(hrv_file_path, header=None, names=['RRIntervals'])
        hrv_data = HRVData(hrv_df, timestamps, os.path.dirname(hrv_file_path), os.path.basename(hrv_file_path))
        # if os.path.basename(participant_path) == 'p04':
        #     hrv_data.print_statistics()
        # hrv_data.print_statistics()

        # Calibration and smoothing
        calib = TemperatureCalibration(
            temp_df,
            self.ground_truth_temperature[os.path.basename(participant_path)],
            temp_columns,
            os.path.basename(temp_file_path),
            os.path.dirname(temp_file_path),
            os.path.join(self.target_dir, os.path.basename(participant_path)),
        )
        calib.smooth_data()
        calib.plot_raw_data()
        self.all_calib_data.append(calib)
        self.all_hrv_data.append(hrv_data)


if __name__ == '__main__':
    data_dir = 'data/study_data_study2'
    target_dir = 'target/study2_results'

    pipeline = Study2Pipeline(data_dir, target_dir)
    pipeline.process_directory()

    raw_data_plotter = RawDataPlotter(pipeline.all_calib_data, pipeline.all_hrv_data, data_dir, target_dir)
    raw_data_plotter.plot_raw_data()

    # hrv_pipeline = HRVPipeline(pipeline.all_hrv_data)
    # hrv_pipeline.analyze()

    # print("Analyzing hypothesis 1")
    # hypothesis1 = Hypothesis1Analyzer(pipeline.all_calib_data, target_dir)
    # hypothesis1.analyze()

    print("Analyzing hypothesis 2")
    hypothesis2 = Hypothesis2Analyzer(pipeline.all_calib_data, pipeline.all_hrv_data, target_dir)
    hypothesis2.analyze()
    hypothesis2.analyze145()

    # print("Analyzing hypothesis 3")
    # hypothesis3 = Hypothesis3Analyzer(pipeline.all_calib_data, pipeline.all_hrv_data, target_dir)
    # hypothesis3.analyze()
    #
    # print("Analyzing hypothesis 4")
    # hypothesis4 = Hypothesis4Analyzer(pipeline.all_calib_data, pipeline.all_hrv_data, target_dir)
    # hypothesis4.analyze()