import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from enum import Enum, auto


class FitType(Enum):
    CONSTANT = auto()
    LINEAR = auto()
    POLY = auto()


class TemperatureCalibration:

    def __init__(self, df, temp_columns, source_filename, data_folder, target_folder):
        self.raw_data = df
        self.temp_columns = temp_columns
        self.raw_data[temp_columns] = self.raw_data[temp_columns] / 100.0
        self.mean_temp = self.raw_data[temp_columns].mean(axis=1)
        self.calibrated_data_dict = {}
        self.source_filename = source_filename
        self.data_folder = data_folder
        self.target_folder = target_folder  # New attribute to store the target folder

    def smooth_data(self):
        self.smoothed_data = self.raw_data.rolling(window=20).mean()

    def apply_constant_fit(self):
        # Precomputed constants for each temperature column
        precomputed_offsets = {
            'Temp01': -0.1428030665607949,
            'Temp02': -0.33519160359189115,
            'Temp03': 0.04000008443548353,
            'Temp04': 0.7531253472670123,
            'Temp05': -0.7074657809141947,
            'Temp06': 0.39233501936436
        }

        # Apply the precomputed constant fit to each column
        for col in self.temp_columns:
            offset = precomputed_offsets[col]
            self.raw_data[col] += offset
        self.calibrated_data_dict["Constant"] = self.raw_data[self.temp_columns]

    def apply_linear_fit_with_precomputed_params(self):
        # Pre-computed linear parameters for each temperature column
        precomputed_params = {
            'Temp01': {'Slope': 0.9146890451740535, 'Intercept': 2.4936977920661705},
            'Temp02': {'Slope': 0.9449294495259986, 'Intercept': 1.377336624239212},
            'Temp03': {'Slope': 0.9278809303064043, 'Intercept': 2.255627428348919},
            'Temp04': {'Slope': 1.1398233398426514, 'Intercept': -3.442787213775257},
            'Temp05': {'Slope': 1.0283003667287702, 'Intercept': -1.5980574312406468},
            'Temp06': {'Slope': 1.053782047439169, 'Intercept': -1.240996774159009}
        }

        # Apply the pre-computed linear fit to each column
        for col in self.temp_columns:
            slope = precomputed_params[col]['Slope']
            intercept = precomputed_params[col]['Intercept']
            self.raw_data[col] = self.raw_data[col] * slope + intercept

        self.calibrated_data_dict["Linear"] = self.raw_data[self.temp_columns]

    def apply_poly_fit_with_precomputed_params(self, degree):
        # Precomputed polynomial coefficients for each temperature column and degree
        coefficients = {
            2: {
                'Temp01': [6.56243818e-04, 8.73903441e-01, 3.11677421e+00],
                'Temp02': [-0.00279603, 1.12003018, -1.32155714],
                'Temp03': [-7.26793306e-04, 9.72810292e-01, 1.57270031e+00],
                'Temp04': [-3.92329035e-02, 3.53002000e+00, -3.94339638e+01],
                'Temp05': [0.01961804, -0.20382259, 17.49935644],
                'Temp06': [0.00847393, 0.53797854, 6.50502162]
            },
            4: {
                'Temp01': [-1.10299685e-03, 1.36947740e-01, -6.33747791e+00, 1.30454320e+02, -9.84255316e+02],
                'Temp02': [-8.97011197e-04, 1.11904789e-01, -5.20876275e+00, 1.08152886e+02, -8.21865150e+02],
                'Temp03': [-1.31204947e-03, 1.61722721e-01, -7.43152289e+00, 1.51806771e+02, -1.13963704e+03],
                'Temp04': [-8.07476964e-04, 1.00175846e-01, -4.67959723e+00, 9.86416947e+01, -7.67193683e+02],
                'Temp05': [2.82941015e-03, -3.60498737e-01, 1.71629635e+01, -3.60751882e+02, 2.84650092e+03],
                'Temp06': [8.30021587e-04, -9.83309053e-02, 4.35448495e+00, -8.44018765e+01, 6.25965166e+02]
            },
            8: {
                'Temp01': [-1.54946212e-07, 2.90172159e-05, -2.06824176e-03, 5.81231371e-02, 5.62050615e-01,
                           -8.54822768e+01, 2.44956219e+03, -3.16867414e+04, 1.61196222e+05],
                'Temp02': [-1.65119315e-07, 3.11410186e-05, -2.23822793e-03, 6.38064322e-02, 5.74349838e-01,
                           -9.26792841e+01, 2.68558171e+03, -3.50355068e+04, 1.79641180e+05],
                'Temp03': [-2.31708982e-07, 4.30171543e-05, -3.04019665e-03, 8.47600731e-02, 8.08890528e-01,
                           -1.22422935e+02, 3.48129735e+03, -4.46895847e+04, 2.25640410e+05],
                'Temp04': [-5.33953625e-07, 9.97409989e-05, -7.15999827e-03, 2.10701271e-01, 1.06598721e+00,
                           -2.58858764e+02, 7.64684951e+03, -9.99881187e+04, 5.11836205e+05],
                'Temp05': [-1.56456589e-06, 2.85391506e-04, -1.98026309e-02, 5.40147954e-01, 5.30420686e+00,
                           -7.66264898e+02, 2.13840313e+04, -2.69971712e+05, 1.34181878e+06],
                'Temp06': [-1.30097369e-06, 2.30770525e-04, -1.55880508e-02, 4.15174128e-01, 3.84937521e+00,
                           -5.52972648e+02, 1.50719769e+04, -1.85744880e+05, 9.01440229e+05]
            },
            16: {
                'Temp01': [8.86074914e-19, -1.12422010e-16, 3.14469389e-15, 9.76655726e-14, -2.34641402e-12,
                           -1.57400186e-10, -8.23737470e-10, 1.74932674e-07, 5.64774636e-06, -8.13413743e-05,
                           -9.32947031e-03, -8.04350639e-02, 1.12999416e+01, 1.78269165e+02, -1.70209641e+04,
                           3.09318092e+05, -1.84866870e+06],
                'Temp02': [5.85580707e-19, -7.57017904e-17, 2.20392749e-15, 6.45189227e-14, -1.72629026e-12,
                           -1.07260573e-10, -3.79541264e-10, 1.24557303e-07, 3.75802368e-06, -6.52338246e-05,
                           -6.49836526e-03, -4.55583787e-02, 8.04300813e+00, 1.14823651e+02, -1.20122137e+04,
                           2.23304618e+05, -1.35643321e+06],
                'Temp03': [1.09523356e-18, -1.38425311e-16, 3.87574597e-15, 1.17868657e-13, -2.87894784e-12,
                           -1.88204186e-10, -9.04120633e-10, 2.07909988e-07, 6.55058528e-06, -9.80818556e-05,
                           -1.07549383e-02, -8.75675182e-02, 1.28734727e+01, 1.96193894e+02, -1.90053891e+04,
                           3.44401296e+05, -2.04907610e+06],
                'Temp04': [-6.02274871e-18, 7.65655890e-16, -2.30608905e-14, -5.42490286e-13, 1.78122209e-11,
                           8.64960862e-10, -1.10031622e-09, -9.96720978e-07, -2.31665610e-05, 6.00697870e-04,
                           4.08114368e-02, 8.28096039e-02, -4.77868145e+01, -4.51674661e+02, 6.22622961e+04,
                           -1.17088148e+06, 7.05624055e+06],
                'Temp05': [2.47710648e-20, 4.10751981e-18, -5.49421632e-16, 1.67371093e-15, 8.28702439e-13,
                           1.51335376e-11, -7.87915315e-10, -4.50645973e-08, -2.54301515e-07, 5.68020280e-05,
                           1.99401036e-03, -3.04053563e-02, -3.49925116e+00, -1.28763694e+00, 5.22279672e+03,
                           -1.22283055e+05, 8.57237278e+05],
                'Temp06': [7.03432879e-19, -8.34841556e-17, 2.15135226e-15, 6.49930816e-14, -1.35825521e-12,
                           -9.07342978e-11, -5.77096704e-10, 8.48221568e-08, 2.76352964e-06, -2.83058313e-05,
                           -3.79121312e-03, -3.99672641e-02, 3.85326144e+00, 6.91588763e+01, -5.18977123e+03,
                           8.31257234e+04, -4.40187555e+05]
            },
            32: {
                'Temp01': [-1.65216523e-45, 1.15586279e-44, 3.74063969e-42, 1.25556138e-40, 2.01633859e-40,
                           -1.76378180e-37, -9.89562436e-36, -2.99599065e-34, -2.84939577e-33, 2.69762897e-31,
                           2.01985263e-29, 8.17643734e-28, 1.98215453e-26, 5.60889725e-27, -2.85183875e-23,
                           -1.72448754e-21, -6.17936349e-20, -1.16594356e-18, 2.12666718e-17, 2.93925336e-15,
                           1.37799365e-13, 3.47888041e-12, -9.65410284e-12, -5.59860809e-09, -2.73819314e-07,
                           -5.20237098e-06, 1.62888962e-04, 1.43670750e-02, 2.77175742e-01, -1.33304711e+01,
                           -6.33072753e+02, 2.39038348e+04, -2.04339559e+05],
                'Temp02': [-2.95925968e-44, 1.80287540e-42, 2.78528160e-41, -9.61833396e-40, -6.38095907e-38,
                           -1.63355426e-36, -1.89953891e-36, 1.85287882e-33, 9.71727958e-32, 2.82686565e-30,
                           3.03018350e-29, -1.91786389e-27, -1.43851543e-25, -5.48753050e-24, -1.18521388e-22,
                           5.40462844e-22, 1.83559326e-19, 9.34337447e-18, 2.66964357e-16, 2.06458743e-15,
                           -2.41264441e-13, -1.51347027e-11, -4.41052989e-10, -1.41744421e-09, 5.14677016e-07,
                           2.41946085e-05, 2.88627500e-04, -2.15363082e-02, -1.00566100e+00, 7.55823183e+00,
                           1.39710279e+03, -3.29474833e+04, 2.15078169e+05],
                'Temp03': [1.86382074e-45, -2.32007775e-43, 1.21842180e-42, 2.97228252e-40, 8.80913648e-39,
                           -1.60355656e-38, -1.27506353e-35, -6.33467055e-34, -1.62797236e-32, -1.34416905e-32,
                           2.21635853e-29, 1.28983595e-27, 4.32632449e-26, 6.87214246e-25, -2.14468401e-23,
                           -2.23216634e-21, -9.93831002e-20, -2.56687476e-18, -5.30075154e-18, 3.37594206e-15,
                           1.96764725e-13, 5.97737146e-12, 3.84297925e-11, -6.59103722e-09, -3.85586416e-07,
                           -8.86159206e-06, 1.62010617e-04, 1.92588771e-02, 4.31455230e-01, -1.63441295e+01,
                           -8.78259953e+02, 3.09220765e+04, -2.55935766e+05],
                'Temp04': [1.01398320e-42, -6.44871998e-41, -7.09427853e-40, 3.85729916e-38, 1.94727927e-36,
                           3.73021081e-35, -4.41195312e-34, -6.08349330e-32, -2.43613095e-30, -5.22035936e-29,
                           1.34414062e-28, 6.69936407e-26, 3.32209848e-24, 9.53274883e-23, 1.09367023e-21,
                           -5.52302387e-20, -4.18634336e-18, -1.52068015e-16, -2.84640603e-15, 3.69801501e-14,
                           5.27591319e-12, 2.15282727e-10, 3.97247841e-09, -7.53635308e-08, -8.15157711e-06,
                           -2.51744981e-04, 3.79870595e-05, 3.05092353e-01, 8.98584649e+00, -1.71692577e+02,
                           -1.30589692e+04, 3.59563805e+05, -2.53886192e+06],
                'Temp05': [6.77987616e-43, -4.66561759e-41, -4.54835509e-40, 3.25009554e-38, 1.56456236e-36,
                           2.74067873e-35, -5.67501347e-34, -5.93468336e-32, -2.27389255e-30, -4.43154888e-29,
                           4.86623502e-28, 8.14749258e-26, 3.78927692e-24, 1.02695651e-22, 7.62862159e-22,
                           -9.05850734e-20, -5.94546905e-18, -2.06023885e-16, -3.36926706e-15, 9.03726926e-14,
                           9.23013787e-12, 3.59591188e-10, 5.95480809e-09, -1.87758671e-07, -1.68876839e-05,
                           -5.05510329e-04, 1.72530327e-03, 7.52396471e-01, 2.18807324e+01, -5.07795094e+02,
                           -3.75171299e+04, 1.14163171e+06, -8.78438649e+06],
                'Temp06': [2.80350379e-43, -1.75920706e-41, -2.05630454e-40, 1.02448203e-38, 5.37937815e-37,
                           1.08324406e-35, -9.88215293e-35, -1.64031258e-32, -6.82998379e-31, -1.54535694e-29,
                           -3.53406626e-30, 1.77076729e-26, 9.28467894e-25, 2.79702766e-23, 3.76445125e-22,
                           -1.34141176e-20, -1.15652344e-18, -4.44979684e-17, -9.19126402e-16, 6.60367026e-15,
                           1.45197042e-12, 6.41661466e-11, 1.33673453e-09, -1.59664339e-08, -2.36677841e-06,
                           -8.12169513e-05, -2.76608503e-04, 9.11674165e-02, 3.07155144e+00, -4.70857796e+01,
                           -4.45413087e+03, 1.17908016e+05, -8.22502671e+05]
            }
        }

        degree_dict = coefficients[degree]  # Get the dictionary for the given degree

        for col in self.temp_columns:
            if col in degree_dict:
                coeffs = degree_dict[col]
                column_name = f"{col}_degree_{degree}"
                self.raw_data[column_name] = np.polyval(coeffs[::-1], self.raw_data[col])
                self.calibrated_data_dict[column_name] = self.raw_data[column_name]

    def plot_fits(self, fit_type):
        # Determine the suffix of the source filename
        source_filename_suffix = os.path.splitext(self.source_filename)[0]

        # Create the folder if it doesn't exist
        os.makedirs(self.data_folder, exist_ok=True)

        # Smoothing the raw data first
        self.smooth_data()
        smoothed_plot_data = self.smoothed_data[self.temp_columns]

        # Create a plot for the smoothed raw data
        plt.figure(figsize=(8, 6), dpi=300)
        plt.plot(smoothed_plot_data)
        plt.xlabel('Sample Index')
        plt.ylabel('Temperature (°C)')
        plt.title('Smoothed Raw Data')
        plt.legend(self.temp_columns, loc='lower right')
        plt.savefig(os.path.join(self.target_folder, f"{source_filename_suffix}_smoothed_raw_data.png"), dpi=300)
        plt.close()

        if fit_type == FitType.CONSTANT:
            plt.figure(figsize=(8, 6), dpi=300)
            plt.plot(self.calibrated_data_dict["Constant"])
            plt.xlabel('Sample Index')
            plt.ylabel('Temperature (°C)')
            plt.title('Constant Fit')
            plt.legend(self.temp_columns, loc='lower right')
            plt.savefig(os.path.join(self.target_folder, f"{source_filename_suffix}_{fit_type.name.lower()}.png"), dpi=300)
            plt.close()

        elif fit_type == FitType.LINEAR:
            plt.figure(figsize=(8, 6), dpi=300)
            plt.plot(self.calibrated_data_dict["Linear"])
            plt.xlabel('Sample Index')
            plt.ylabel('Temperature (°C)')
            plt.title('Linear Fit')
            plt.legend(self.temp_columns, loc='lower right')
            plt.savefig(os.path.join(self.target_folder, f"{source_filename_suffix}_{fit_type.name.lower()}.png"), dpi=300)
            plt.close()

        elif fit_type == FitType.POLY:
            # Create a plot for each set of calibrated data (by polynomial degree)
            unique_degrees = set(
                name.split('_')[-1].replace("degree_", "") for name in self.calibrated_data_dict.keys())

            for degree in unique_degrees:
                plt.figure(figsize=(8, 6), dpi=300)

                for temp_col in self.temp_columns:
                    column_name = f"{temp_col}_degree_{degree}"
                    calibrated_data = self.calibrated_data_dict.get(column_name, None)

                    if calibrated_data is not None:
                        plt.plot(calibrated_data)

                plt.xlabel('Sample Index')
                plt.ylabel('Temperature (°C)')
                plt.title(f"Polynomial Fit Degree {degree}")
                plt.legend(self.temp_columns, loc='lower right')
                plt.savefig(os.path.join(self.target_folder, f"{source_filename_suffix}_{fit_type.name.lower()}_degree_{degree}.png"), dpi=300)
                plt.close()


class AnalysisPipeline:

    def __init__(self, data_dir, target_dir, fit_type):
        self.data_dir = data_dir
        self.target_dir = target_dir
        self.fit_type = fit_type

    def process_directory(self, dir_path, target_path):
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            item_target_path = os.path.join(target_path, item)
            if os.path.isdir(item_path):
                os.makedirs(item_target_path, exist_ok=True)
                self.process_directory(item_path, item_target_path)
            elif item_path.endswith('.csv'):
                self.process_file(item_path, item_target_path)

    def process_file(self, file_path, target_path):
        print(f"Processing file: {file_path}")
        df = pd.read_csv(file_path)
        temp_columns = ['Temp01', 'Temp02', 'Temp03', 'Temp04', 'Temp05', 'Temp06']

        # Get only the directory path for the target
        target_dir = os.path.dirname(target_path)

        calib = TemperatureCalibration(df, temp_columns, os.path.basename(file_path), os.path.dirname(file_path),
                                       target_dir)
        calib.smooth_data()

        if self.fit_type == FitType.CONSTANT:
            calib.apply_constant_fit()
        elif self.fit_type == FitType.LINEAR:
            calib.apply_linear_fit_with_precomputed_params()
        elif self.fit_type == FitType.POLY:
            for degree in [2, 4, 8, 16, 32]:
                calib.apply_poly_fit_with_precomputed_params(degree)

        calib.plot_fits(self.fit_type)


if __name__ == '__main__':
    data_dir = 'data'
    target_dir = 'target'
    fit_type = FitType.CONSTANT
    pipeline = AnalysisPipeline(data_dir, target_dir, fit_type)
    pipeline.process_directory(data_dir, target_dir)
