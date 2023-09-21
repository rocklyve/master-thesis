from scipy import stats
import numpy as np


class Hypothesis2Analyzer:
    def __init__(self, raw_data, temp_columns, hypothesis2_results_by_phase):
        self.raw_data = raw_data
        self.temp_columns = temp_columns
        self.hypothesis2_results_by_phase = hypothesis2_results_by_phase

    def aggregate_results_for_hypothesis2(self, results_by_phase):
        """
        Aggregate results across all participants for hypothesis 2.
        This includes calculating mean standard deviations for each condition (indoor and outdoor).
        """
        aggregated_results = {'Indoor': [], 'Outdoor': []}

        for participant, phase_results in results_by_phase.items():
            for phase_id, stats in phase_results.items():
                if stats['condition'] in ['Indoor', 'Outdoor']:
                    aggregated_results[stats['condition']].append(stats['std_all'])

        aggregated_stats = {
            'global_std_indoor': np.mean(aggregated_results['Indoor']),
            'global_std_outdoor': np.mean(aggregated_results['Outdoor'])
        }

        return aggregated_stats

    def test_hypothesis2_by_phase(self):
        """
        Test the second hypothesis by phase:
        The fluctuations in temperature readings are less indoors than outdoors.

        Metrics:
        - Standard Deviation
        - t-test for significance of variance
        """
        results_by_phase = {}

        # Get unique phase IDs
        unique_ids = self.raw_data['ID'].unique()

        for phase_id in unique_ids:
            phase_data = self.raw_data[self.raw_data['ID'] == phase_id]
            std_all = phase_data[self.temp_columns].std().mean()

            # Condition (indoor or outdoor) based on phase ID
            condition = 'Indoor' if phase_id == 2 else 'Outdoor' if phase_id == 3 else 'Unknown'

            results_by_phase[phase_id] = {
                'std_all': std_all,
                'condition': condition
            }

        return results_by_phase
