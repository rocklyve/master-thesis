from collections import defaultdict
from datetime import timedelta
import numpy as np
from scipy import stats
import pandas as pd
import copy


class Hypothesis2Analyzer:
    def __init__(self, all_temp_data, all_hrv_data, target_dir):
        self.all_temp_data = all_temp_data
        self.all_hrv_data = all_hrv_data
        self.target_dir = target_dir

    def perform_ttest(self, sample1, sample2):
        t_stat, p_value = stats.ttest_rel(sample1, sample2)
        return t_stat, p_value

    def analyze(self):
        stress_test_temp_data = {}
        stroop_values = defaultdict(list)
        nback_values = defaultdict(list)
        math_values = defaultdict(list)
        stress_test_temp_data = {}  # To store the mean temperature for each stress test and sensor for all probands

        for temp_data in self.all_temp_data:
            proband = temp_data.source_filename.split('_')[2].split('.')[0]  # Extract proband name from filename
            ground_truth = temp_data.ground_truth_temp  # Extract ground truth for the current proband

            for stress_test in ['Stroop', 'N-Back', 'Math']:  # Loop through the stress tests
                range_start, range_end = self.get_time_range_for_stress_test(stress_test, temp_data,
                                                                             self.all_hrv_data[0])
                # stress_test_data = temp_data.raw_data[(temp_data.raw_data['TIMESTAMP'] >= range_start) and (temp_data.raw_data['TIMESTAMP'] <= range_end)]  # Filter data for the current stress test
                stress_test_data = temp_data.raw_data[
                    (temp_data.raw_data['TIMESTAMP'] >= range_start) & (temp_data.raw_data['TIMESTAMP'] <= range_end)]

                # print last timestamp of temp_data.raw_data

                for sensor in temp_data.temp_columns:  # Loop through each sensor
                    # mean_temp = stress_test_data[
                    #     sensor].mean()  # Calculate mean temperature for the current sensor and stress test
                    # remove nan values from stress_test_data[sensor]
                    mean_temp = np.nanmean(stress_test_data[sensor].values)
                    mean_temp -= ground_truth  # Subtract the ground truth temperature

                    if stress_test not in stress_test_temp_data:
                        stress_test_temp_data[stress_test] = {}

                    if sensor not in stress_test_temp_data[stress_test]:
                        stress_test_temp_data[stress_test][sensor] = []

                    stress_test_temp_data[stress_test][sensor].append(mean_temp)

        # Generate LaTeX table or plots based on stress_test_temp_data
        # ...

        for sensor, temps in stress_test_temp_data['Stroop'].items():
            stroop_values[sensor].append(temps)
        for sensor, temps in stress_test_temp_data['N-Back'].items():
            nback_values[sensor].append(temps)
        for sensor, temps in stress_test_temp_data['Math'].items():
            math_values[sensor].append(temps)

        # Perform t-tests
        for sensor in self.all_temp_data[0].temp_columns:
            t_stat_stroop_nback, p_value_stroop_nback = self.perform_ttest(stroop_values[sensor][0],
                                                                           nback_values[sensor][0])
            t_stat_nback_math, p_value_nback_math = self.perform_ttest(nback_values[sensor][0], math_values[sensor][0])

            print(
                f"For sensor {sensor}, t-statistic and p-value between Stroop and N-Back are {t_stat_stroop_nback} and {p_value_stroop_nback} respectively.")
            print(
                f"For sensor {sensor}, t-statistic and p-value between N-Back and Math are {t_stat_nback_math} and {p_value_nback_math} respectively.")

        # self.create_latex_table(stress_test_temp_data, filename_suffix='_all')  # For all probands

        # For Stroop-N-Back
        self.create_latex_table_2(stress_test_temp_data, ['Stroop', 'N-Back'], filename_suffix='_stroop_nback')

        # For N-Back-Math
        self.create_latex_table_2(stress_test_temp_data, ['N-Back', 'Math'], filename_suffix='_nback_math')

    def analyze145(self):
        stress_test_temp_data = {}
        stroop_values = defaultdict(list)
        nback_values = defaultdict(list)
        math_values = defaultdict(list)
        stress_test_temp_data = {}  # To store the mean temperature for each stress test and sensor for all probands

        for temp_data in self.all_temp_data:
            proband = temp_data.source_filename.split('_')[2].split('.')[0]  # Extract proband name from filename
            if proband not in ['p01', 'p04', 'p05']:
                continue
            ground_truth = temp_data.ground_truth_temp  # Extract ground truth for the current proband

            for stress_test in ['Stroop', 'N-Back', 'Math']:  # Loop through the stress tests
                range_start, range_end = self.get_time_range_for_stress_test(stress_test, temp_data,
                                                                             self.all_hrv_data[0])
                # stress_test_data = temp_data.raw_data[(temp_data.raw_data['TIMESTAMP'] >= range_start) and (temp_data.raw_data['TIMESTAMP'] <= range_end)]  # Filter data for the current stress test
                stress_test_data = temp_data.raw_data[
                    (temp_data.raw_data['TIMESTAMP'] >= range_start) & (temp_data.raw_data['TIMESTAMP'] <= range_end)]

                # print last timestamp of temp_data.raw_data

                for sensor in temp_data.temp_columns:  # Loop through each sensor
                    # mean_temp = stress_test_data[
                    #     sensor].mean()  # Calculate mean temperature for the current sensor and stress test
                    # remove nan values from stress_test_data[sensor]
                    mean_temp = np.nanmean(stress_test_data[sensor].values)
                    mean_temp -= ground_truth  # Subtract the ground truth temperature

                    if stress_test not in stress_test_temp_data:
                        stress_test_temp_data[stress_test] = {}

                    if sensor not in stress_test_temp_data[stress_test]:
                        stress_test_temp_data[stress_test][sensor] = []

                    stress_test_temp_data[stress_test][sensor].append(mean_temp)

        # At the end of the loop that populates stress_test_temp_data
        for sensor, temps in stress_test_temp_data['Stroop'].items():
            stroop_values[sensor].append(temps)
        for sensor, temps in stress_test_temp_data['N-Back'].items():
            nback_values[sensor].append(temps)
        for sensor, temps in stress_test_temp_data['Math'].items():
            math_values[sensor].append(temps)

        # Perform t-tests
        for sensor in self.all_temp_data[0].temp_columns:
            t_stat_stroop_nback, p_value_stroop_nback = self.perform_ttest(stroop_values[sensor][0],
                                                                           nback_values[sensor][0])
            t_stat_nback_math, p_value_nback_math = self.perform_ttest(nback_values[sensor][0], math_values[sensor][0])

            print(
                f"For sensor {sensor}, t-statistic and p-value between Stroop and N-Back are {t_stat_stroop_nback} and {p_value_stroop_nback} respectively.")
            print(
                f"For sensor {sensor}, t-statistic and p-value between N-Back and Math are {t_stat_nback_math} and {p_value_nback_math} respectively.")



        self.create_latex_table(stress_test_temp_data, filename_suffix='_all')  # For all probands

    def get_time_range_for_stress_test(self, stress_test, temp_data, hrv_data):
        # Assuming hrv_data has a dictionary 'hrv_timestamps' containing the start times of each stress test
        # and temp_data has a field 'start' with the timestamp of the start of the recording
        if stress_test == 'Stroop':
            start_time = hrv_data.hrv_timestamps["stroop_start"]
            end_time = hrv_data.hrv_timestamps["n-back_start"]
        elif stress_test == 'N-Back':
            start_time = hrv_data.hrv_timestamps["n-back_start"]
            end_time = hrv_data.hrv_timestamps["math_start"]
        else:
            start_time = hrv_data.hrv_timestamps["math_start"]
            end_time = hrv_data.hrv_timestamps["stress_end"]

        # Convert these times to the same unit as temp_data.raw_data['Timestamp'] (e.g., milliseconds from the start of the recording)
        start_time_ms = self.convert_to_ms(start_time)
        end_time_ms = self.convert_to_ms(end_time)

        return start_time_ms / 1000 / 60, end_time_ms / 1000 / 60

    def convert_to_ms(self, time_str):
        minutes, seconds = map(int, time_str.split(':'))
        total_seconds = timedelta(minutes=minutes, seconds=seconds).total_seconds()
        return int(total_seconds * 1000)  # Convert to milliseconds

    def create_latex_table(self, stress_test_temp_data, filename_suffix=''):
        for stress_test, sensor_data in stress_test_temp_data.items():
            for sensor, temps in sensor_data.items():
                stress_test_temp_data[stress_test][sensor] = round(np.mean(temps), 2)

        # Create the LaTeX table
        latex_code = "\\begin{table}[t]\n\\centering\n\\begin{tabular}{|l|rrr|}\n\\hline\n"
        latex_code += "Sensor & Stroop Test & N-Back Test & Math Test \\\\\n"
        latex_code += "& Mean Temp & Mean Temp & Mean Temp \\\\\n\\hline\n"

        for sensor in ['TympanicMembrane', 'Concha', 'EarCanal', 'Out_Bottom', 'Out_Top', 'Out_Middle']:
            latex_code += f"{sensor} & "
            for stress_test in ['Stroop', 'N-Back', 'Math']:
                mean_temp = stress_test_temp_data[stress_test].get(sensor, 'N/A')
                latex_code += f"{mean_temp} & "
            latex_code = latex_code.rstrip(" & ")  # Remove trailing ampersands and spaces
            latex_code += " \\\\\n"

        latex_code += "\\hline\n\\end{tabular}\n"
        latex_code += "\\caption{Mean Temperature of each stress test over all participants. "
        latex_code += "The measured ground truth values are subtracted from each participants temperature data to combine the results in a more fair way.}\n"
        latex_code += f"\\label{{subsec:Evaluation:Study2:Hypothesis2:mean{filename_suffix}_participants}}\n\\end{{table}}"

        print("LaTeX code:")
        print(latex_code)
        return latex_code

    def create_latex_table_2(self, stress_test_temp_data, tests, filename_suffix=''):
        # Initialize a dictionary to store the temperature differences
        temp_diff_data = defaultdict(lambda: defaultdict(list))

        # Calculate the temperature differences for each proband and sensor
        for sensor in stress_test_temp_data[tests[0]].keys():
            for i in range(len(stress_test_temp_data[tests[0]][sensor])):
                temp_diff = stress_test_temp_data[tests[1]][sensor][i] - stress_test_temp_data[tests[0]][sensor][i]
                temp_diff_data[sensor][f'p0{i + 1}'].append(temp_diff)

        # Create the LaTeX table
        latex_code = "\\begin{table}[t]\n\\centering\n\\begin{tabular}{|l|" + "r" * len(
            temp_diff_data.keys()) + "|}\n\\hline\n"
        latex_code += "Participant & " + " & ".join(temp_diff_data.keys()) + " \\\\\n\\hline\n"

        for participant in temp_diff_data[next(iter(temp_diff_data))].keys():
            latex_code += f"{participant} & "
            for sensor in temp_diff_data.keys():
                mean_diff = round(np.mean(temp_diff_data[sensor][participant]), 2)
                latex_code += f"{mean_diff} & "
            latex_code = latex_code.rstrip(" & ")  # Remove trailing ampersands and spaces
            latex_code += " \\\\\n"

        latex_code += "\\hline\n\\end{tabular}\n"
        latex_code += f"\\caption{{Temperature differences between {tests[0]} and {tests[1]} for each participant.}}\n"
        latex_code += f"\\label{{subsec:Evaluation:Study2:Hypothesis2:temp_diff{filename_suffix}}}\n\\end{{table}}"

        print("LaTeX code:")
        print(latex_code)
        return latex_code