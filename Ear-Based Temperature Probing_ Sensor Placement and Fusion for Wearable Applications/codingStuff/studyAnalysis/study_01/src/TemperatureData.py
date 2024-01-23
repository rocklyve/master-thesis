import os
from scipy import stats
import seaborn as sns
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


class TemperatureData:

    def __init__(self, df, temp_columns, source_filename, data_folder, target_folder, real_temp_ground_truth):
        self.raw_data = df
        self.real_temp_ground_truth = real_temp_ground_truth
        self.temp_columns = temp_columns
        self.raw_data[temp_columns] = self.raw_data[temp_columns] / 100.0
        self.raw_data['TIMESTAMP'] = (self.raw_data['TIMESTAMP'] - self.raw_data['TIMESTAMP'].min()) / 1000.0 / 60.0
        self.mean_temp = self.raw_data[temp_columns].mean(axis=1)
        self.source_filename = source_filename
        self.data_folder = data_folder
        self.target_folder = target_folder  # New attribute to store the target folder

    def smooth_data(self):
        self.smoothed_data = self.raw_data.rolling(window=120, min_periods=1).mean()

    def plot_raw_data(self):
        # Mapping for renaming sensor labels
        rename_map = {
            'TympanicMembrane': 'Tympanic Membrane',
            'Concha': 'Concha',
            'EarCanal': 'Ear Canal',
            'Out_Bottom': 'Outer Ear Bottom',
            'Out_Top': 'Outer Ear Top',
            'Out_Middle': 'Outer Ear Middle'
        }

        def add_background_color(ax):
            custom_colors = ["#CCCCE5", "#CCE5FF", "#E5FFE4", "#FFE9C9", "#FFFFFF", "#FFFFFF"]
            unique_ids = self.raw_data['ID'].unique()
            # colors = sns.color_palette("husl", len(unique_ids))
            for i, unique_id in enumerate(unique_ids):
                id_data = self.raw_data[self.raw_data['ID'] == unique_id]
                ax.axvspan(id_data['TIMESTAMP'].min(), id_data['TIMESTAMP'].max(), facecolor=custom_colors[i], alpha=1)

        source_filename_suffix = os.path.splitext(self.source_filename)[0]
        os.makedirs(self.data_folder, exist_ok=True)
        self.smooth_data()

        melted_smoothed_data = pd.melt(self.smoothed_data, id_vars=['TIMESTAMP'],
                                       value_vars=self.temp_columns, var_name='Sensor',
                                       value_name='Temperature')

        plt.figure(figsize=(10, 5), dpi=300)
        ax = plt.gca()

        # Use a visually appealing color palette
        # sns.set_palette(custom_colors)
        # sns.set_palette("coolwarm", n_colors=len(self.temp_columns))

        sns.lineplot(x='TIMESTAMP', y='Temperature', hue='Sensor',
                     data=melted_smoothed_data, ax=ax, dashes=False, linewidth=1.25, alpha=0.95)

        add_background_color(ax)

        ax.grid(False)
        plt.xlabel('Time (min)', fontsize=14)
        plt.ylabel('Temperature (°C)', fontsize=14)
        subject = self.source_filename.split('_')[2].split('.')[0]
        gt = str(self.real_temp_ground_truth)
        plt.title('Raw Data of Subject ' + subject + " (Ground Truth: " + gt + "°C)", fontsize=16)
        plt.xlim(self.raw_data['TIMESTAMP'].min(), self.raw_data['TIMESTAMP'].max())  # New line here

        # Rename and resize the legend
        handles, labels = ax.get_legend_handles_labels()
        renamed_labels = [rename_map.get(label, label) for label in labels]
        plt.legend(handles, renamed_labels, title='Temperature Sensors', loc='lower right', fontsize='small')

        plt.savefig(os.path.join(self.target_folder, f"{source_filename_suffix}_0smoothed_raw_data.png"), dpi=300, bbox_inches='tight')
        plt.close()
