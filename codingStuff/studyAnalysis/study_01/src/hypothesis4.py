import numpy as np


class Hypothesis4Analyzer:
    def __init__(self, all_temp_data):
        self.all_temp_data = all_temp_data

    def analyze(self):
        stability_metrics = {}
        subject_count = 0

        for temp_data in self.all_temp_data:
            subject_count += 1
            for phase in [2, 3]:  # Only consider Phases 2 and 3
                phase_key = f"Phase{phase}"
                if phase_key not in stability_metrics:
                    stability_metrics[phase_key] = {}

                phase_data = temp_data.raw_data[temp_data.raw_data['ID'] == phase]
                if phase_data.empty:
                    continue

                for sensor in temp_data.temp_columns:
                    # Calculate the standard deviation for each sensor's readings
                    std_dev = np.std(phase_data[sensor])

                    if sensor not in stability_metrics[phase_key]:
                        stability_metrics[phase_key][sensor] = 0.0

                    stability_metrics[phase_key][sensor] += std_dev

        # Calculate mean standard deviation across all subjects
        for phase_key in stability_metrics:
            for sensor in stability_metrics[phase_key]:
                stability_metrics[phase_key][sensor] /= subject_count

        print(stability_metrics)

        return stability_metrics
