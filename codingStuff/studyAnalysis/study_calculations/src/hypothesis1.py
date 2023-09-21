import numpy as np
from scipy import stats


def calculate_mae(list1, list2):
    return np.mean(np.abs(np.array(list1) - np.array(list2)))


class Hypothesis1Analyzer:
    def __init__(self, raw_data, temp_columns, aggregated_results_by_phase):
        self.raw_data = raw_data
        self.temp_columns = temp_columns
        self.aggregated_results_by_phase = aggregated_results_by_phase

    # This function calculates the Mean Absolute Error between two lists

    def aggregate_results_across_participants(self, hypothesis1_results_by_phase):
        """
        Aggregate results across all participants for hypothesis 1.
        This could include calculating global means, standard deviations, etc.
        """
        # Initialize aggregation variables
        for phase_id, stats in hypothesis1_results_by_phase.items():
            if phase_id not in self.aggregated_results_by_phase:
                self.aggregated_results_by_phase[phase_id] = {
                    'mean_behind_ear': [],
                    'std_behind_ear': [],
                    'mean_other': [],
                    'std_other': []
                }

            self.aggregated_results_by_phase[phase_id]['mean_behind_ear'].append(stats['mean_behind_ear'])
            self.aggregated_results_by_phase[phase_id]['std_behind_ear'].append(stats['std_behind_ear'])
            self.aggregated_results_by_phase[phase_id]['mean_other'].append(stats['mean_other'])
            self.aggregated_results_by_phase[phase_id]['std_other'].append(stats['std_other'])

    def aggregate_results_by_phase(self):
        """
        Aggregate results across all participants for hypothesis 1, by each phase.
        This includes calculating mean and standard deviations for each phase.
        """
        aggregated_results = {}

        for phase_id, stats in self.aggregated_results_by_phase.items():
            global_mean_behind_ear = np.mean(stats['mean_behind_ear'])
            global_mean_other = np.mean(stats['mean_other'])

            mae = calculate_mae(stats['mean_behind_ear'], stats['mean_other'])
            global_mae_behind_ear = np.mean(np.abs(np.array(stats['mean_behind_ear']) - global_mean_behind_ear))
            global_mae_other = np.mean(np.abs(np.array(stats['mean_other']) - global_mean_other))

            aggregated_results[phase_id] = {
                'global_mean_behind_ear': global_mean_behind_ear,
                'global_std_behind_ear': np.mean(stats['std_behind_ear']),
                'global_mean_other': global_mean_other,
                'global_std_other': np.mean(stats['std_other']),
                'global_mae': mae,
                'global_mae_behind_ear': global_mae_behind_ear,
                'global_mae_other': global_mae_other
            }
        return aggregated_results
