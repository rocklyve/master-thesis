from scipy import stats
import numpy as np


class Hypothesis2Analyzer:
    def __init__(self, all_temp_data):
        self.all_temp_data = all_temp_data

    def analyze(self):
        variances_by_sensor = {'Indoor': {}, 'Outdoor': {}}
        diff_from_ground_truth = {'Indoor': {}, 'Outdoor': {}}
        diff_from_mean = {'Indoor': {}, 'Outdoor': {}}
        num_tests = 0  # Keep track of the number of tests

        for temp_data in self.all_temp_data:
            indoor_data = temp_data.raw_data[temp_data.raw_data['ID'] == 2]
            outdoor_data = temp_data.raw_data[temp_data.raw_data['ID'] == 3]

            ground_truth = temp_data.real_temp_ground_truth

            for sensor in temp_data.temp_columns:
                indoor_mean = np.mean(indoor_data[sensor])
                indoor_var = np.var(indoor_data[sensor])
                outdoor_mean = np.mean(outdoor_data[sensor])
                outdoor_var = np.var(outdoor_data[sensor])

                indoor_diff_from_gt = indoor_mean - ground_truth
                outdoor_diff_from_gt = outdoor_mean - ground_truth

                if sensor not in variances_by_sensor['Indoor']:
                    variances_by_sensor['Indoor'][sensor] = []
                if sensor not in variances_by_sensor['Outdoor']:
                    variances_by_sensor['Outdoor'][sensor] = []

                variances_by_sensor['Indoor'][sensor].append(indoor_var)
                variances_by_sensor['Outdoor'][sensor].append(outdoor_var)

                if sensor not in diff_from_ground_truth['Indoor']:
                    diff_from_ground_truth['Indoor'][sensor] = []
                if sensor not in diff_from_ground_truth['Outdoor']:
                    diff_from_ground_truth['Outdoor'][sensor] = []

                diff_from_ground_truth['Indoor'][sensor].append(indoor_diff_from_gt)
                diff_from_ground_truth['Outdoor'][sensor].append(outdoor_diff_from_gt)

                num_tests += 1

        # Calculations and output
        for sensor in self.all_temp_data[0].temp_columns:
            mean_indoor_var = np.mean([x for x in variances_by_sensor['Indoor'][sensor] if not np.isnan(x)])
            mean_outdoor_var = np.mean([x for x in variances_by_sensor['Outdoor'][sensor] if not np.isnan(x)])
            mean_indoor_diff_from_gt = np.mean([x for x in diff_from_ground_truth['Indoor'][sensor] if not np.isnan(x)])
            mean_outdoor_diff_from_gt = np.mean([x for x in diff_from_ground_truth['Outdoor'][sensor] if not np.isnan(x)])

            print(f"Mean Variance for {sensor} (Indoor): {mean_indoor_var}")
            print(f"Mean Variance for {sensor} (Outdoor): {mean_outdoor_var}")
            print(f"Mean Difference from Ground Truth for {sensor} (Indoor): {mean_indoor_diff_from_gt}")
            print(f"Mean Difference from Ground Truth for {sensor} (Outdoor): {mean_outdoor_diff_from_gt}")

        # T-test to compare variances
        alpha = 0.05
        bonferroni_alpha = alpha / num_tests  # Bonferroni corrected alpha

        for sensor in self.all_temp_data[0].temp_columns:
            # Remove NaNs if present
            indoor_var_clean = [x for x in variances_by_sensor['Indoor'][sensor] if not np.isnan(x)]
            outdoor_var_clean = [x for x in variances_by_sensor['Outdoor'][sensor] if not np.isnan(x)]

            t_stat, p_value = stats.ttest_ind(indoor_var_clean, outdoor_var_clean)

            if p_value < bonferroni_alpha:
                print(f"Reject null hypothesis for {sensor}: p-value = {p_value}, t-stat = {t_stat}")
            else:
                print(f"Fail to reject null hypothesis for {sensor}: p-value = {p_value}, t-stat = {t_stat}")

        print("Variance by sensor:")
        print(variances_by_sensor)

        print("Diff from ground truth by sensor:")
        print(diff_from_ground_truth)
