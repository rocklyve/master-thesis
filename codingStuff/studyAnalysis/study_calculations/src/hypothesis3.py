# for Hypothesis 3, you can use Pearson's correlation coefficient to test
# the relationship between relative changes in temperature readings from
# different sensor locations.
import numpy as np
from scipy.stats import spearmanr  # or use pearsonr, depending on your data distribution
import numpy as np


class Hypothesis3Analyzer:
    def __init__(self, all_calib_data):
        self.all_calib_data = all_calib_data

    def analyze(self):
        correlation_matrix = {}  # To store correlation coefficients for each sensor pair

        # Loop through all TemperatureCalibration objects
        for calib in self.all_calib_data:
            sensor_data = calib.raw_data[calib.temp_columns]  # Access sensor data

            for i, sensor1 in enumerate(calib.temp_columns):
                for j, sensor2 in enumerate(calib.temp_columns):
                    if i >= j:
                        continue  # Skip duplicate and self-comparisons

                    # Calculate relative changes for these sensors
                    readings1 = sensor_data[sensor1].dropna().values  # Remove NaNs
                    readings2 = sensor_data[sensor2].dropna().values
                    if len(readings1) == 0 or len(readings2) == 0:
                        continue  # Skip if no data

                    rel_changes1 = self.calculate_relative_changes(readings1)
                    rel_changes2 = self.calculate_relative_changes(readings2)

                    # Calculate Spearman correlation for relative changes
                    corr_coeff, _ = spearmanr(rel_changes1, rel_changes2)

                    # Store in correlation_matrix
                    pair_key = f"{sensor1}-{sensor2}"
                    if pair_key not in correlation_matrix:
                        correlation_matrix[pair_key] = []
                    correlation_matrix[pair_key].append(corr_coeff)

        # Now average the correlation coefficients for each pair of sensors
        avg_correlations = {key: np.mean(values) for key, values in correlation_matrix.items()}

        print("Average correlations:")
        print(avg_correlations)

        return avg_correlations  # Return average correlations for interpretation

    def calculate_relative_changes(self, readings):
        # Calculate relative changes for a single sensor
        # Assuming readings is a numpy array
        rel_changes = np.diff(readings) / readings[:-1] * 100  # In percentage
        return rel_changes
