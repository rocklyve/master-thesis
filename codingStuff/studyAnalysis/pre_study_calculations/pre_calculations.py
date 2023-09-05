# Description: This file contains the pre-calculations for the study
from src.explorative_plot import ExplorativePlot
from src.explorative_plot_concat import ExplorativePlotConcat
from src.explorative_plot_incl_offset import ExplorativePlotInclOffset
from src.explorative_plot_with_offset import ExplorativePlotWithOffset
from src.explorative_plot_with_offset_lin_function import ExplorativePlotWithOffsetLinFunction
from src.explorative_plot_with_offset_poly_function import ExplorativePlotWithOffsetPolyFunction
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
        # self.explorative_plot.execute("explorative_plot")
        self.explorative_plot_concat.execute("explorative_plot_concat")
        # self.explorative_plot_incl_offset.execute("explorative_plot_incl_offset")
        # self.explorative_plot_with_offset.execute("explorative_plot_with_offset")
        # self.explorative_plot_with_offset_lin_function.execute("explorative_plot_with_offset_lin_function")
        # self.explorative_plot_with_offset_poly_function.execute("explorative_plot_with_offset_poly_function")
        # self.explorative_plot_mean_offset.execute()


if __name__ == "__main__":
    main_instance = PreCalculations()
    main_instance.execute()
    exit(0)
