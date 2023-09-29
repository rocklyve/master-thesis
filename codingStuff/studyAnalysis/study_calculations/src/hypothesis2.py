from scipy import stats
import numpy as np


class Hypothesis2Analyzer:
    def __init__(self, all_calib_data):
        self.all_calib_data = all_calib_data

    def analyze(self):
        variances_by_sensor = {'Indoor': {}, 'Outdoor': {}}
        num_tests = 0  # Keep track of the number of tests

        for calib_data in self.all_calib_data:
            indoor_data = calib_data.raw_data[calib_data.raw_data['ID'] == 2]
            outdoor_data = calib_data.raw_data[calib_data.raw_data['ID'] == 3]

            for sensor in calib_data.temp_columns:
                indoor_var = indoor_data[sensor].var()
                outdoor_var = outdoor_data[sensor].var()

                if sensor not in variances_by_sensor['Indoor']:
                    variances_by_sensor['Indoor'][sensor] = []
                if sensor not in variances_by_sensor['Outdoor']:
                    variances_by_sensor['Outdoor'][sensor] = []

                variances_by_sensor['Indoor'][sensor].append(indoor_var)
                variances_by_sensor['Outdoor'][sensor].append(outdoor_var)

                num_tests += 1

        alpha = 0.05
        bonferroni_alpha = alpha / num_tests  # Bonferroni corrected alpha

        for sensor in calib_data.temp_columns:
            # Remove NaNs if present
            indoor_var_clean = [x for x in variances_by_sensor['Indoor'][sensor] if not np.isnan(x)]
            outdoor_var_clean = [x for x in variances_by_sensor['Outdoor'][sensor] if not np.isnan(x)]

            t_stat, p_value = stats.ttest_ind(indoor_var_clean, outdoor_var_clean)

            if p_value < bonferroni_alpha:
                print(f"Reject null hypothesis for {sensor}: p-value = {p_value}")
            else:
                print(f"Fail to reject null hypothesis for {sensor}: p-value = {p_value}")

        print("Analyzing hypothesis 2")
        print(variances_by_sensor)
