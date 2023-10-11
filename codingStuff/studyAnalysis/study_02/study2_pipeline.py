import os
import pandas as pd
from study_02.src.TemperatureCalibration import TemperatureCalibration
from study_02.src.hrv_pipeline import HRVPipeline
import numpy as np

from study_02.src.hypothesis1 import Hypothesis1Analyzer
from study_02.src.hypothesis2 import Hypothesis2Analyzer
from study_02.src.hypothesis3 import Hypothesis3Analyzer
from study_02.src.hypothesis4 import Hypothesis4Analyzer
from study_02.src.hypothesis5 import Hypothesis5Analyzer
from study_02.src.hypothesis6 import Hypothesis6Analyzer
from study_02.src.raw_data_plotter import RawDataPlotter


class Study2Pipeline:
    def __init__(self, data_dir, target_dir):
        self.data_dir = data_dir
        self.target_dir = target_dir
        self.all_calib_data = []
        self.all_hrv_data = []

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
        hrv_df = pd.read_csv(hrv_file_path, header=None, names=['RRIntervals'])

        # Calibration and smoothing
        calib = TemperatureCalibration(
            temp_df,
            temp_columns,
            os.path.basename(temp_file_path),
            os.path.dirname(temp_file_path),
            os.path.join(self.target_dir, os.path.basename(participant_path)),
        )
        calib.smooth_data()
        calib.plot_raw_data()
        self.all_calib_data.append(calib)
        self.all_hrv_data.append(hrv_df)


if __name__ == '__main__':
    data_dir = 'data/study_data_study2'
    target_dir = 'target/study2_results'

    pipeline = Study2Pipeline(data_dir, target_dir)
    pipeline.process_directory()

    raw_data_plotter = RawDataPlotter(pipeline.all_calib_data, pipeline.all_hrv_data, data_dir, target_dir)
    raw_data_plotter.plot_raw_data()

    print("Analyzing hypothesis 1")
    hypothesis1 = Hypothesis1Analyzer(pipeline.all_calib_data, pipeline.all_hrv_data, target_dir)
    hypothesis1.analyze()

    print("Analyzing hypothesis 2")
    hypothesis2 = Hypothesis2Analyzer(pipeline.all_calib_data, pipeline.all_hrv_data, target_dir)
    hypothesis2.analyze()

    print("Analyzing hypothesis 3")
    hypothesis3 = Hypothesis3Analyzer(pipeline.all_calib_data, pipeline.all_hrv_data, target_dir)
    hypothesis3.analyze()

    print("Analyzing hypothesis 4")
    hypothesis4 = Hypothesis4Analyzer(pipeline.all_calib_data, pipeline.all_hrv_data, target_dir)
    hypothesis4.analyze()

    print("Analyzing hypothesis 5")
    hypothesis5 = Hypothesis5Analyzer(pipeline.all_calib_data, pipeline.all_hrv_data, target_dir)
    hypothesis5.analyze()

    print("Analyzing hypothesis 6")
    hypothesis6 = Hypothesis6Analyzer(pipeline.all_calib_data, pipeline.all_hrv_data, target_dir)
    hypothesis6.analyze()