import numpy as np
from scipy.stats import ttest_rel


class Hypothesis4Analyzer:
    def __init__(self, all_temp_data):
        self.all_temp_data = all_temp_data

    def analyze(self):
        stability_metrics = {'Phase2': {}, 'Phase3': {}}
        stability_sums = {'Phase2': {}, 'Phase3': {}}
        p_values = {}
        subject_count = 0

        for temp_data in self.all_temp_data:
            subject_count += 1
            for phase in [2, 3]:  # Only consider Phases 2 and 3
                phase_key = f"Phase{phase}"

                phase_data = temp_data.raw_data[temp_data.raw_data['ID'] == phase]
                if phase_data.empty:
                    continue

                for sensor in temp_data.temp_columns:
                    # Calculate the standard deviation for each sensor's readings
                    std_dev = np.std(phase_data[sensor])

                    if sensor not in stability_metrics[phase_key]:
                        stability_metrics[phase_key][sensor] = []
                        stability_sums[phase_key][sensor] = 0.0

                    stability_metrics[phase_key][sensor].append(std_dev)
                    stability_sums[phase_key][sensor] += std_dev

        # Average the standard deviations across all subjects
        for phase_key in stability_sums:
            for sensor in stability_sums[phase_key]:
                stability_sums[phase_key][sensor] /= subject_count

        # Perform paired t-tests for each sensor
        for sensor in self.all_temp_data[0].temp_columns:  # Assuming temp_columns is the same for all temp_data
            phase2_values = stability_metrics['Phase2'].get(sensor, [])
            phase3_values = stability_metrics['Phase3'].get(sensor, [])

            if len(phase2_values) == len(phase3_values) and len(phase2_values) > 1:
                t_stat, p_value = ttest_rel(phase2_values, phase3_values)
                p_values[sensor] = p_value

        print(f"Stability metrics (mean standard deviation) for Phases 2 and 3: {stability_sums}")
        print(f"P-values for paired t-test between Phase 2 and Phase 3: {p_values}")

        return stability_sums, p_values
