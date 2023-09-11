# Description: This file contains the pre-calculations for the study
from src.explorative_plot import ExplorativePlot
from src.explorative_plot_concat import ExplorativePlotConcat
from src.explorative_plot_incl_offset import ExplorativePlotInclOffset
from src.explorative_plot_with_offset import ExplorativePlotWithOffset
from src.explorative_plot_with_offset_lin_function import ExplorativePlotWithOffsetLinFunction
from src.explorative_plot_with_offset_poly_function import ExplorativePlotWithOffsetPolyFunction
from src.calibration_pipeline.calibration_pipeline import CalibrationPipeline
from src.mean_offset import ExplorativePlotMeanOffset

class PreCalculations:
    def __init__(self):
        self.explorative_plot = ExplorativePlot()
        self.explorative_plot_concat = ExplorativePlotConcat()
        self.explorative_plot_incl_offset = ExplorativePlotInclOffset()
        self.explorative_plot_with_offset = ExplorativePlotWithOffset()
        self.explorative_plot_with_offset_lin_function = ExplorativePlotWithOffsetLinFunction()
        self.explorative_plot_with_offset_poly_function = ExplorativePlotWithOffsetPolyFunction()
        self.explorative_plot_mean_offset = ExplorativePlotMeanOffset()

    def execute(self):
        file_paths = [
            'data/Logging_08_30_Ultimaker_25_degree_Metall.csv',
            'data/Logging_08_30_Ultimaker_30_degree_Metall.csv',
            'data/Logging_08_30_Ultimaker_35_degree_Metall.csv',
            'data/Logging_08_30_Ultimaker_40_degree_Metall.csv',
            'data/Logging_08_30_Ultimaker_45_degree_Metall.csv'
        ]
        temp_columns = ['Temp01', 'Temp02', 'Temp03', 'Temp04', 'Temp05', 'Temp06']
        # Create and run the pipeline
        pipeline = CalibrationPipeline(file_paths, temp_columns, 'target/fit_parameters.json')
        pipeline.run_pipeline()


if __name__ == "__main__":
    main_instance = PreCalculations()
    main_instance.execute()
    exit(0)
