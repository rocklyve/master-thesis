import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from enum import Enum, auto
import json

class FitType(Enum):
    CONSTANT = auto()
    LINEAR = auto()
    POLY = auto()


class TemperatureCalibration:

    def __init__(self, df, temp_columns, source_filename, data_folder, target_folder, json_path):
        self.raw_data = df
        self.temp_columns = temp_columns
        self.raw_data[temp_columns] = self.raw_data[temp_columns] / 100.0
        self.raw_data['TIMESTAMP'] = (self.raw_data['TIMESTAMP'] - self.raw_data['TIMESTAMP'].min()) / 1000.0 / 60.0
        self.mean_temp = self.raw_data[temp_columns].mean(axis=1)
        self.calibrated_data_dict = {}
        self.source_filename = source_filename
        self.data_folder = data_folder
        self.target_folder = target_folder  # New attribute to store the target folder

        # Read precomputed constants from JSON file
        with open(json_path, 'r') as f:
            self.json_constants = json.load(f)

    def smooth_data(self):
        self.smoothed_data = self.raw_data.rolling(window=20).mean()

    def apply_constant_fit(self):
        # Precomputed constants for each temperature column

        precomputed_offsets = self.json_constants['precomputed_offsets']

        # Apply the precomputed constant fit to each column
        for col in self.temp_columns:
            offset = precomputed_offsets[col]
            self.raw_data[col] += offset
        self.calibrated_data_dict["Constant"] = self.raw_data[self.temp_columns]

    def apply_linear_fit_with_precomputed_params(self):
        # Pre-computed linear parameters for each temperature column

        precomputed_params = self.json_constants['precomputed_params']

        # Apply the pre-computed linear fit to each column
        for col in self.temp_columns:
            slope = precomputed_params[col]['Slope']
            intercept = precomputed_params[col]['Intercept']
            self.raw_data[col] = self.raw_data[col] * slope + intercept

        self.calibrated_data_dict["Linear"] = self.raw_data[self.temp_columns]

    def apply_poly_fit_with_precomputed_params(self, degree):
        # Get the dictionary for the given degree
        degree_dict = self.json_constants['coefficients'].get(str(degree), {})

        for col in self.temp_columns:
            if col in degree_dict:
                coeffs = degree_dict[col]
                column_name = f"{col}_degree_{degree}"
                self.raw_data[column_name] = np.polyval(coeffs, self.raw_data[col])
                self.calibrated_data_dict[column_name] = self.raw_data[column_name]

    def plot_fits(self, fit_type):
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

        if fit_type == FitType.CONSTANT:
            plt.figure(figsize=(8, 6), dpi=300)
            ax = plt.gca()
            plt.plot(self.raw_data['TIMESTAMP'], self.calibrated_data_dict["Constant"])
            add_background_color(ax)
            plt.xlabel('Time (min)')
            plt.ylabel('Temperature (°C)')
            plt.title('Constant Fit')
            plt.legend(self.temp_columns, loc='lower right')
            plt.savefig(os.path.join(self.target_folder, f"{source_filename_suffix}_{fit_type.name.lower()}.png"), dpi=300)
            plt.close()

        elif fit_type == FitType.LINEAR:
            plt.figure(figsize=(8, 6), dpi=300)
            ax = plt.gca()
            plt.plot(self.raw_data['TIMESTAMP'], self.calibrated_data_dict["Linear"])
            add_background_color(ax)
            plt.xlabel('Time (min)')
            plt.ylabel('Temperature (°C)')
            plt.title('Linear Fit')
            plt.legend(self.temp_columns, loc='lower right')
            plt.savefig(os.path.join(self.target_folder, f"{source_filename_suffix}_{fit_type.name.lower()}.png"), dpi=300)
            plt.close()

        elif fit_type == FitType.POLY:
            # Create a plot for each set of calibrated data (by polynomial degree)
            unique_degrees = set(
                name.split('_')[-1].replace("degree_", "") for name in self.calibrated_data_dict.keys())

            for degree in unique_degrees:
                plt.figure(figsize=(8, 6), dpi=300)

                ax = plt.gca()

                for temp_col in self.temp_columns:
                    column_name = f"{temp_col}_degree_{degree}"
                    calibrated_data = self.calibrated_data_dict.get(column_name, None)

                    if calibrated_data is not None:
                        plt.plot(self.raw_data['TIMESTAMP'], calibrated_data)

                add_background_color(ax)

                plt.xlabel('Time (min)')
                plt.ylabel('Temperature (°C)')
                plt.title(f"Polynomial Fit Degree {degree}")
                plt.legend(self.temp_columns, loc='lower right')
                plt.savefig(os.path.join(self.target_folder, f"{source_filename_suffix}_{fit_type.name.lower()}_degree_{degree}.png"), dpi=300)
                plt.close()


class AnalysisPipeline:

    def __init__(self, data_dir, target_dir, fit_type):
        self.data_dir = data_dir
        self.target_dir = target_dir
        self.fit_type = fit_type

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
        df = df.iloc[3000:]
        df = df.iloc[:-500]
        temp_columns = ['TympanicMembrane', 'Concha', 'EarCanal', 'Out_Bottom', 'Out_Top', 'Out_Middle']

        # Get only the directory path for the target
        target_dir = os.path.dirname(target_path)

        calib = TemperatureCalibration(df, temp_columns, os.path.basename(file_path), os.path.dirname(file_path),
                                       target_dir, 'fit_parameters.json')
        calib.smooth_data()

        if self.fit_type == FitType.CONSTANT:
            calib.apply_constant_fit()
        elif self.fit_type == FitType.LINEAR:
            calib.apply_linear_fit_with_precomputed_params()
        elif self.fit_type == FitType.POLY:
            for degree in [2, 4, 8, 16, 32]:
                calib.apply_poly_fit_with_precomputed_params(degree)

        calib.plot_fits(self.fit_type)


if __name__ == '__main__':
    data_dir = 'data'
    target_dir = 'target'

    fit_type = FitType.CONSTANT
    pipeline = AnalysisPipeline(data_dir, target_dir, fit_type)
    pipeline.process_directory(data_dir, target_dir)

    pipeline.fit_type = FitType.LINEAR
    pipeline.process_directory(data_dir, target_dir)

    pipeline.fit_type = FitType.POLY
    pipeline.process_directory(data_dir, target_dir)
