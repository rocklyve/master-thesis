from scipy.stats import f_oneway


class Hypothesis4Analyzer:
    def __init__(self, all_calib_data):
        self.all_calib_data = all_calib_data

    def analyze(self):
        activity_effects = {}
        for calib in self.all_calib_data:
            # Filter data to only include phase 3 (ID=3) for physical activity
            phase3_data = calib.raw_data[calib.raw_data['ID'] == 3]
            if phase3_data.empty:
                continue

            for sensor in calib.temp_columns:
                # Perform one-way ANOVA between sensor readings in phase 3 and other phases
                groups = []
                for activity in calib.raw_data['ID'].unique():
                    activity_data = calib.raw_data[calib.raw_data['ID'] == activity]
                    groups.append(activity_data[sensor].dropna().values)

                # Perform one-way ANOVA
                f_value, p_value = f_oneway(*groups)

                # Apply Bonferroni correction
                p_value_corrected = p_value * len(groups)
                p_value_corrected = min(p_value_corrected, 1)  # Ensure p_value <= 1

                activity_effects[f"{sensor}-F_value"] = f_value
                activity_effects[f"{sensor}-P_value"] = p_value_corrected

        return activity_effects
