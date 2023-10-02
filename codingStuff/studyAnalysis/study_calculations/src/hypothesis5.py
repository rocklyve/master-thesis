import numpy as np
from scipy.stats import f_oneway


class Hypothesis5Analyzer:
    def __init__(self, all_calib_data):
        self.all_calib_data = all_calib_data

    def analyze(self):
        stability_metrics = {}
        for calib in self.all_calib_data:
            for phase in [2, 3]:  # Only consider Phases 2 and 3
                phase_data = calib.raw_data[calib.raw_data['ID'] == phase]
                if phase_data.empty:
                    continue

                phase_stability_metrics = {}
                for sensor in calib.temp_columns:
                    # Calculate the standard deviation for each sensor's readings
                    std_dev = np.std(phase_data[sensor])
                    phase_stability_metrics[sensor] = std_dev

                stability_metrics[f"Phase{phase}"] = phase_stability_metrics
                print(stability_metrics)

        return stability_metrics