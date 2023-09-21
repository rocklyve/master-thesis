import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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

    def plot_fits(self):
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


class AnalysisPipeline:

    def __init__(self, data_dir, target_dir):
        self.data_dir = data_dir
        self.target_dir = target_dir

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
        calib.plot_fits()


if __name__ == '__main__':
    data_dir = 'data/study_data'
    target_dir = 'target'

    pipeline = AnalysisPipeline(data_dir, target_dir)
    pipeline.process_directory(data_dir, target_dir)