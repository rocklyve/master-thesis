import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import ttest_rel


# Define the Hypothesis1Analyzer class
class Hypothesis1Analyzer:
    def __init__(self, all_calib_data, target_dir):
        self.all_calib_data = all_calib_data  # List of TemperatureCalibration objects
        self.target_dir = target_dir  # Directory where plots will be saved

    def analyze(self):
        mean_temp_list = []  # To store the mean temperature for each phase and sensor for all probands
        organized_data = {}  # Nested dictionary to organize data for t-test

        for calib_data in self.all_calib_data:
            proband = calib_data.source_filename.split('_')[2].split('.')[0] # Extract proband name from filename
            ground_truth = calib_data.ground_truth_temp  # Extract ground truth for the current proband

            for phase_id in [2, 3, 4]:  # Loop through the phase IDs (sitting, stress, relax)
                phase_data = calib_data.raw_data[
                    calib_data.raw_data['ID'] == phase_id]  # Filter data for the current phase

                for sensor in calib_data.temp_columns:  # Loop through each sensor
                    mean_temp = phase_data[sensor].mean()  # Calculate mean temperature for the current sensor and phase
                    mean_temp -= ground_truth  # Subtract the ground truth temperature

                    mean_temp_list.append({
                        'Proband': proband,
                        'Phase': phase_id,
                        'Sensor': sensor,
                        'Mean_Temperature': mean_temp
                    })

        # Create LaTeX tables
        self.create_latex_table(mean_temp_list, filename_suffix='_all')  # For all probands
        self.create_latex_table(mean_temp_list, probands=['p01', 'p04', 'p05'], filename_suffix='_145')  # For probands 1, 4, and 5

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
