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
        self.smoothed_data = self.raw_data.rolling(window=120, min_periods=1).mean()

    def plot_raw_data(self):
        # Determine the suffix of the source filename
        source_filename_suffix = os.path.splitext(self.source_filename)[0]

        # Create the folder if it doesn't exist
        os.makedirs(self.data_folder, exist_ok=True)

        # Smoothing the raw data first
        self.smooth_data()
        smoothed_plot_data = self.smoothed_data[self.temp_columns]

        # Filter data for IDs greater than 1
        filtered_data = self.raw_data[self.raw_data['ID'] > 1]
        filtered_smoothed_data = smoothed_plot_data.loc[filtered_data.index]

        def add_background_color(ax):
            # Only consider IDs greater than 1
            unique_ids = [i for i in self.raw_data['ID'].unique() if i > 1]
            colors = plt.cm.jet(np.linspace(0, 1, len(unique_ids)))
            for i, unique_id in enumerate(unique_ids):
                id_data = self.raw_data[self.raw_data['ID'] == unique_id]
                ax.axvspan(id_data['TIMESTAMP'].min(), id_data['TIMESTAMP'].max(), facecolor=colors[i], alpha=0.2,
                           label=f'ID {unique_id}')

        # Create a plot for the smoothed raw data
        plt.figure(figsize=(8, 6), dpi=300)
        ax = plt.gca()
        if not filtered_smoothed_data.isna().all().all():  # Check if all values are NaN
            plt.plot(filtered_data['TIMESTAMP'], filtered_smoothed_data)
        add_background_color(ax)
        plt.xlabel('Time (min)')
        plt.ylabel('Temperature (°C)')
        plt.title('Smoothed Raw Data')
        plt.legend(self.temp_columns, loc='lower right')
        plt.savefig(os.path.join(self.target_folder, f"{source_filename_suffix}_0smoothed_raw_data.png"), dpi=300)
        plt.close()