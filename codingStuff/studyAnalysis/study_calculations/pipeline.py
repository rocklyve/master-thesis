import os
import glob
import enum
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class FitType(enum.Enum):
    CONSTANT = 1
    LINEAR = 2
    POLY_2 = 3
    POLY_4 = 4
    POLY_8 = 5
    POLY_16 = 6
    POLY_32 = 7

class AnalyzationPipeline:
    def __init__(self, root_data_dir, temp_columns, fit_type):
        self.root_data_dir = root_data_dir
        self.temp_columns = temp_columns
        self.fit_type = fit_type
        self.file_paths = glob.glob(f"{root_data_dir}/**/*.csv", recursive=True)

    def read_csv(self, file_path):
        return pd.read_csv(file_path, delimiter=',')

    def apply_fit(self, data, fit_type):
        # Your fit logic here, for example, for a constant fit:
        if fit_type == FitType.CONSTANT:
            return data - data.mean()
        # Similarly, add conditions for other fit types
        return data

    def plot_and_save(self, data, relative_path):
        target_path = f"target/{relative_path}"
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        plt.figure()
        plt.plot(data)
        plt.savefig(f"{target_path}.png", dpi=300)

    def run_pipeline(self):
        for file_path in self.file_paths:
            data = self.read_csv(file_path)
            calibrated_data = self.apply_fit(data[self.temp_columns], self.fit_type)
            relative_path = os.path.relpath(file_path, self.root_data_dir)
            file_name = os.path.splitext(relative_path)[0]
            self.plot_and_save(calibrated_data, file_name)

# Example usage
root_data_dir = 'data'
temp_columns = ['Temp01', 'Temp02', 'Temp03', 'Temp04', 'Temp05', 'Temp06']
fit_type = FitType.CONSTANT  # or FitType.LINEAR, FitType.POLY_2, etc.

pipeline = AnalyzationPipeline(root_data_dir, temp_columns, fit_type)
pipeline.run_pipeline()
