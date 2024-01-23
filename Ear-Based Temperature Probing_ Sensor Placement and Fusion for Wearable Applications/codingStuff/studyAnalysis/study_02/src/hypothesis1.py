import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import ttest_rel


# Define the Hypothesis1Analyzer class
class Hypothesis1Analyzer:
    def __init__(self, all_temp_data, target_dir):
        self.all_temp_data = all_temp_data
        self.target_dir = target_dir  # Directory where plots will be saved

    def analyze(self):
        mean_temp_list = []  # To store the mean temperature for each phase and sensor for all probands
        organized_data = {}  # Nested dictionary to organize data for t-test

        for temp_data in self.all_temp_data:
            proband = temp_data.source_filename.split('_')[2].split('.')[0] # Extract proband name from filename
            ground_truth = temp_data.ground_truth_temp  # Extract ground truth for the current proband

            for phase_id in [2, 3, 4]:  # Loop through the phase IDs (sitting, stress, relax)
                phase_data = temp_data.raw_data[
                    temp_data.raw_data['ID'] == phase_id]  # Filter data for the current phase

                for sensor in temp_data.temp_columns:  # Loop through each sensor
                    mean_temp = phase_data[sensor].mean()  # Calculate mean temperature for the current sensor and phase
                    mean_temp -= ground_truth  # Subtract the ground truth temperature

                    mean_temp_list.append({
                        'Proband': proband,
                        'Phase': phase_id,
                        'Sensor': sensor,
                        'Mean_Temperature': mean_temp
                    })

        # Create LaTeX tables
        # self.create_latex_table(mean_temp_list, filename_suffix='_all')  # For all probands
        # self.create_latex_table(mean_temp_list, probands=['p01', 'p04', 'p05'], filename_suffix='_145')  # For probands 1, 4, and 5

        self.create_latex_table_2(mean_temp_list, filename_suffix='_all')  # For all probands
        # self.create_latex_table_2(mean_temp_list, probands=['p01', 'p04', 'p05'],
        #                           filename_suffix='_145')  # For probands 1, 4, and 5

        # Organize the data
        for entry in mean_temp_list:
            sensor = entry['Sensor']
            phase = entry['Phase']
            mean_temp = entry['Mean_Temperature']

            if entry['Proband'] not in ['p01', 'p04', 'p05']:
                continue

            if sensor not in organized_data:
                organized_data[sensor] = {}

            if phase not in organized_data[sensor]:
                organized_data[sensor][phase] = []

            organized_data[sensor][phase].append(mean_temp)

        # Perform t-tests
        for sensor, phase_data in organized_data.items():
            sitting_data = np.array(phase_data.get(2, []))  # Phase ID for 'Sitting'
            stress_data = np.array(phase_data.get(3, []))  # Phase ID for 'Stress'
            relax_data = np.array(phase_data.get(4, []))  # Phase ID for 'Stress'

            print('Now for sitting - stress')
            t_stat, p_value = self.perform_ttest(sitting_data, stress_data)

            print(f"For sensor {sensor}, t-statistic is {t_stat} and p-value is {p_value}")

            print('Now for stress - relax')
            t_stat, p_value = self.perform_ttest(stress_data, relax_data)

            print(f"For sensor {sensor}, t-statistic is {t_stat} and p-value is {p_value}")

    def perform_ttest(self, data1, data2):
        t_stat, p_value = ttest_rel(data1, data2, nan_policy='omit')  # 'omit' will ignore NaNs
        return t_stat, p_value

    def create_latex_table_2(self, mean_temp_list, probands=None, filename_suffix=''):
        # Initialize a dictionary to store the temperature differences
        sensor_phase_diff_data = {}

        # Filter data based on the specified probands, if any
        if probands is not None:
            mean_temp_list = [entry for entry in mean_temp_list if entry['Proband'] in probands]

        # Populate the sensor_phase_diff_data dictionary
        for entry in mean_temp_list:
            proband = entry['Proband']
            sensor = entry['Sensor']
            phase = entry['Phase']
            mean_temp = entry['Mean_Temperature']

            if proband not in sensor_phase_diff_data:
                sensor_phase_diff_data[proband] = {}

            if sensor not in sensor_phase_diff_data[proband]:
                sensor_phase_diff_data[proband][sensor] = {}

            sensor_phase_diff_data[proband][sensor][phase] = mean_temp

        # Create the LaTeX tables
        for table_title, (phase1, phase2) in zip(['Sitting to Stress', 'Stress to Relax'], [(2, 3), (3, 4)]):
            latex_code = "\\begin{table}[t]\n\\centering\n\\begin{tabular}{|l|" + "r" * len(
                self.all_temp_data[0].temp_columns) + "|}\n\\hline\n"
            latex_code += "Proband & " + ' & '.join(self.all_temp_data[0].temp_columns) + " \\\\\n\\hline\n"

            for proband, sensor_data in sensor_phase_diff_data.items():
                row_data = []
                for sensor in self.all_temp_data[0].temp_columns:
                    temp_diff = round(
                        sensor_data.get(sensor, {}).get(phase2, np.nan) - sensor_data.get(sensor, {}).get(phase1,
                                                                                                          np.nan), 2)
                    row_data.append(str(temp_diff) if not np.isnan(temp_diff) else 'N/A')

                latex_code += f"{proband} & {' & '.join(row_data)} \\\\\n"

            latex_code += "\\hline\n\\end{tabular}\n"
            latex_code += f"\\caption{{Temperature Difference from {table_title} for each participant.}}\n"
            latex_code += f"\\label{{subsec:Evaluation:Study2:Hypothesis1:temp_diff_{table_title.replace(' ', '_').lower()}{filename_suffix}}}\n\\end{{table}}"

            print(f"LaTeX code for {table_title}:")
            print(latex_code)

    def create_latex_table(self, mean_temp_list, probands=None, filename_suffix=''):
        # Initialize a dictionary to store the mean temperatures
        sensor_phase_data = {}

        # Filter data based on the specified probands, if any
        if probands is not None:
            mean_temp_list = [entry for entry in mean_temp_list if entry['Proband'] in probands]

        # Populate the sensor_phase_data dictionary
        for entry in mean_temp_list:
            sensor = entry['Sensor']
            phase = entry['Phase']
            mean_temp = entry['Mean_Temperature']

            if sensor not in sensor_phase_data:
                sensor_phase_data[sensor] = {}

            if phase not in sensor_phase_data[sensor]:
                sensor_phase_data[sensor][phase] = []

            sensor_phase_data[sensor][phase].append(mean_temp)

        # Calculate the mean temperature for each sensor and phase
        for sensor, phase_data in sensor_phase_data.items():
            for phase, temps in phase_data.items():
                sensor_phase_data[sensor][phase] = round(np.mean(temps), 2)

        # Create the LaTeX table
        latex_code = "\\begin{table}[t]\n\\centering\n\\begin{tabular}{|l|rrr|}\n\\hline\n"
        latex_code += "Sensor & Sitting Phase & Stress Phase & Relax Phase \\\\\n"
        latex_code += "& Mean Temp & Mean Temp & Mean Temp \\\\\n\\hline\n"

        for sensor, phase_data in sensor_phase_data.items():
            sitting_temp = phase_data.get(2, 'N/A')
            stress_temp = phase_data.get(3, 'N/A')
            relax_temp = phase_data.get(4, 'N/A')
            latex_code += f"{sensor} & {sitting_temp} & {stress_temp} & {relax_temp} \\\\\n"

        latex_code += "\\hline\n\\end{tabular}\n"
        latex_code += "\\caption{Mean Temperature of each phase over all participants. "
        latex_code += "The measured ground truth values is subtracted from each participants temperature data to combine the results in a more fair way.}\n"
        latex_code += f"\\label{{subsec:Evaluation:Study2:Hypothesis1:mean{filename_suffix}_participants}}\n\\end{{table}}"

        print("LaTeX code:")
        print(latex_code)
        return latex_code