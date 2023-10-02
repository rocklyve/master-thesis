from scipy.stats import f_oneway


# Bewegung, gemessen durch IMU-Signale, führt zu kurzfristigen Veränderungen in den Temperaturmesswerten.
class Hypothesis7Analyzer:
    def __init__(self, all_calib_data):
        self.all_calib_data = all_calib_data

    def analyze(self):
        pass