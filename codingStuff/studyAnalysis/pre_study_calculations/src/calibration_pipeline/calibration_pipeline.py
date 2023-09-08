# class which starts a pipeline for the calibration of the different temperature sensors

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import mean_absolute_error


class CalibrationPipeline:
    def __init__(self, file_paths, temp_columns):
        self.file_paths = file_paths
        self.temp_columns = temp_columns
        self.concatenated_df = None
        self.smoothed_data = None
        self.mean_temp = None
        self.calibrated_data_dict = {}
        self.mae_values = {}
        self.correlation_values = {}
        self.mae_and_variance = {}

    def read_and_concatenate_data(self):
        self.concatenated_df = pd.DataFrame()
        for file_path in self.file_paths:
            df = pd.read_csv(file_path)
            df[self.temp_columns] = df[self.temp_columns] / 100
            self.concatenated_df = pd.concat([self.concatenated_df, df[self.temp_columns]], ignore_index=True)

    def plot_raw_data(self):
        plt.figure()
        plt.plot(self.concatenated_df)
        plt.title('Concatenated Raw Temperature Curves')
        plt.xlabel('Sample Index')
        plt.ylabel('Temperature (°C)')
        plt.legend(self.temp_columns)
        plt.savefig("target/concatenated_raw_plot.png")

    def smooth_data(self):
        window_size = int(len(self.concatenated_df.index) / 50)
        min_periods = int(len(self.concatenated_df.index) / 200)
        self.smoothed_data = self.concatenated_df[self.temp_columns].rolling(window=window_size,
                                                                             min_periods=min_periods,
                                                                             center=True).mean()
        self.mean_temp = self.smoothed_data.mean(axis=1)

    def apply_calibration(self):
        selected_degrees = [2, 4, 8, 16, 32]
        constant_calibrated = self.smoothed_data.copy()
        overall_mean = self.mean_temp.mean()  # Mean of the average temperature at each time point

        for col in self.temp_columns:
            curve_mean = self.smoothed_data[col].mean()  # Mean of this particular curve
            offset = overall_mean - curve_mean  # Offset to adjust this curve's mean to the overall mean
            constant_calibrated[col] = self.smoothed_data[col] + offset  # Apply the offset

        self.calibrated_data_dict['Constant'] = constant_calibrated
        linear_calibrated = self.smoothed_data.copy()

        for col in self.temp_columns:
            slope, intercept = np.polyfit(self.smoothed_data[col].dropna(), self.mean_temp.dropna(), 1)
            linear_calibrated[col] = slope * self.smoothed_data[col] + intercept

        self.calibrated_data_dict['Linear'] = linear_calibrated

        for degree in selected_degrees:
            poly_calibrated = self.smoothed_data.copy()
            for col in self.temp_columns:
                np_polyfit = np.polyfit(self.smoothed_data[col].dropna(), self.mean_temp.dropna(), degree)
                poly_calibrated[col] = np.polyval(np_polyfit, self.smoothed_data[col])
            self.calibrated_data_dict[f'Poly_{degree}'] = poly_calibrated

    def plot_calibrated_data(self):
        for name, calibrated_data in self.calibrated_data_dict.items():
            plt.figure()
            plt.plot(calibrated_data)
            plt.title(f'Calibrated Temperature Curves ({name})')
            plt.xlabel('Sample Index')
            plt.ylabel('Temperature (°C)')
            plt.legend(self.temp_columns)
            plt.savefig(f"target/concatenated_fit_{name}.png")

    def calculate_mae(self):
        for name, calibrated_data in self.calibrated_data_dict.items():
            mae = np.mean([mean_absolute_error(self.mean_temp.dropna(), calibrated_data[col].dropna()) for col in
                           self.temp_columns])
            self.mae_values[name] = mae

    def plot_mae_boxplot(self):
        mae_list_by_method = {}
        for name, calibrated_data in self.calibrated_data_dict.items():
            mae_list = [mean_absolute_error(self.mean_temp.dropna(), calibrated_data[col].dropna()) for col in
                        self.temp_columns]
            mae_list_by_method[name] = mae_list
        plt.figure()
        plt.boxplot(mae_list_by_method.values(), labels=mae_list_by_method.keys())
        plt.title('Boxplot of MAE by Calibration Method')
        plt.ylabel('MAE')
        plt.xlabel('Calibration Method')
        plt.savefig("target/concatenated_box_plot.png")

    def calculate_correlation(self):
        for name, calibrated_data in self.calibrated_data_dict.items():
            correlation = np.mean([calibrated_data[col].corr(self.mean_temp) for col in self.temp_columns])
            self.correlation_values[name] = correlation

    def calculate_mae_and_variance(self):
        for name, calibrated_data in self.calibrated_data_dict.items():
            mae = np.mean([mean_absolute_error(self.mean_temp.dropna(), calibrated_data[col].dropna()) for col in
                           self.temp_columns])
            variance = np.var([mean_absolute_error(self.mean_temp.dropna(), calibrated_data[col].dropna()) for col in
                               self.temp_columns])
            self.mae_and_variance[name] = {'MAE': mae, 'Variance': variance}

    def plot_all_fits_together(self):
        # Create a subplot layout
        num_subplots = 1 + len(self.calibrated_data_dict)  # 1 for raw data + number of fits
        fig, axs = plt.subplots(4, 2, sharex=True, figsize=(12, 16), dpi=300)  # Adjusted for A4 and high DPI

        axs = axs.flatten()  # Flatten the 2D array to 1D for easy indexing

        # Plot raw data
        axs[0].plot(self.smoothed_data)
        axs[0].text(0.05, 0.9, 'Smoothed Raw Data', transform=axs[0].transAxes)  # Custom title

        # Plot each fit
        for i, (name, calibrated_data) in enumerate(self.calibrated_data_dict.items(), start=1):
            axs[i].plot(calibrated_data)
            axs[i].text(0.05, 0.9, f"{name} Fit", transform=axs[i].transAxes)  # Custom title

        # Common labels and title
        for ax in axs:
            ax.set_xlabel('Sample Index')
        axs[0].set_ylabel('Temperature (°C)')

        # Add legend to the last subplot only
        axs[-1].legend(self.temp_columns, loc='lower right')

        # Save the plot
        plt.tight_layout()

        # Save the plot with high DPI
        plt.savefig("target/concatenated_all_fits.png", dpi=300)  # Increased DPI for higher resolution

    def print_fit_parameters(self):
        print("Fit Parameters:")

        # Constant Fit (it's just an offset, so one parameter)
        print("\nConstant Fit:")
        overall_mean = self.mean_temp.mean()
        for col in self.temp_columns:
            curve_mean = self.smoothed_data[col].mean()
            offset = overall_mean - curve_mean
            print(f"{col}: Offset = {offset}")

        # Linear Fit (two parameters: slope and intercept)
        print("\nLinear Fit:")
        for col in self.temp_columns:
            slope, intercept = np.polyfit(self.smoothed_data[col].dropna(), self.mean_temp.dropna(), 1)
            print(f"{col}: Slope = {slope}, Intercept = {intercept}")

        # Polynomial Fits (coefficients)
        selected_degrees = [2, 4, 8, 16, 32]
        for degree in selected_degrees:
            print(f"\nPolynomial Fit (degree {degree}):")
            for col in self.temp_columns:
                coefficients = np.polyfit(self.smoothed_data[col].dropna(), self.mean_temp.dropna(), degree)
                print(f"{col}: Coefficients = {coefficients}")

    def run_pipeline(self):
        self.read_and_concatenate_data()
        self.plot_raw_data()
        self.smooth_data()
        self.apply_calibration()
        self.plot_calibrated_data()
        self.calculate_mae()
        self.plot_mae_boxplot()
        self.calculate_correlation()
        self.calculate_mae_and_variance()
        self.plot_all_fits_together()
        self.print_fit_parameters()

        print("MAE values:", self.mae_values)
        print("Correlation values:", self.correlation_values)
        print("MAE and Variance:", self.mae_and_variance)
