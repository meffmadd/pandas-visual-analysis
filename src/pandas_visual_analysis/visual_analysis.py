import typing
import warnings

from pandas import DataFrame

from pandas_visual_analysis.data_source import DataSource
from pandas_visual_analysis.layout import AnalysisLayout
from pandas_visual_analysis.utils.config import Config
from pandas_visual_analysis.utils.util import hex_to_rgb
import pandas_visual_analysis.utils.validation as validate


class VisualAnalysis:
    """
    Generate linked plots that support brushing from a pandas.DataFrame and display them in Jupyter notebooks.

    :param data: the pandas.DataFrame object or a :class:`DataSource`
    :param layout: layout specification name or explicit definition of plot in rows
    :param categorical_columns: if given, specifies which columns are to be interpreted as categorical
    :param row_height: height in pixels each row and consequently each plot should have
    :param sample: int or float specifying if the DataFrame should be sub-sampled.
        When an int is given, the DataFrame will be limited to that number of rows given by the value.
        When a float is given, the DataFrame will include the fraction of rows given by the value.
    :param select_color: RGB tuple or hex color specifying the color display selected data points
    :param deselect_color: RGB tuple or hex color specifying the color display deselected data points
    :param alpha: opacity of data points
    """

    def __init__(
        self,
        data: typing.Union[DataFrame, DataSource],
        layout: typing.Union[str, typing.List[typing.List[str]]] = "default",
        categorical_columns: typing.Union[typing.List[str], None] = None,
        row_height: int = 400,
        sample: typing.Union[float, int, None] = None,
        select_color: typing.Union[str, typing.Tuple[int, int, int]] = "#323EEC",
        deselect_color: typing.Union[str, typing.Tuple[int, int, int]] = "#8A8C93",
        alpha: float = 0.75,
    ):
        super().__init__()

        validate.validate_data(data)
        validate.validate_alpha(alpha)
        validate.validate_color(select_color)
        validate.validate_color(deselect_color)

        if isinstance(select_color, str):
            self.select_color: typing.Tuple[int, int, int] = hex_to_rgb(select_color)
        elif isinstance(select_color, tuple):
            self.select_color: typing.Tuple[int, int, int] = select_color

        if isinstance(deselect_color, str):
            self.deselect_color: typing.Tuple[int, int, int] = hex_to_rgb(
                deselect_color
            )
        elif isinstance(deselect_color, tuple):
            self.deselect_color: typing.Tuple[int, int, int] = deselect_color

        self.alpha = alpha
        self.color_scale = [
            [0, "rgb(%d,%d,%d)" % self.deselect_color],
            [1, "rgb(%d,%d,%d)" % self.select_color],
        ]

        config = Config()
        config["alpha"] = self.alpha
        config["select_color"] = self.select_color
        config["deselect_color"] = self.deselect_color
        config["color_scale"] = self.color_scale

        if isinstance(data, DataFrame):
            self.data_source = DataSource(
                df=data, categorical_columns=categorical_columns, sample=sample
            )
        elif isinstance(data, DataSource):
            self.data_source = data

        self.layout = AnalysisLayout(
            layout=layout, row_height=row_height, data_source=self.data_source
        )

        if self.data_source.few_num_cols and len(self._check_numerical_plots()) != 0:
            warnings.warn(
                "The passed DataFrame only has %d NUMERICAL column, which is insufficient for some plots "
                "like Parallel Coordinates. These plots will not be displayed."
                % len(self.data_source.numerical_columns)
            )

        if self.data_source.few_cat_cols and len(self._check_categorical_plots()) != 0:
            warnings.warn(
                "The passed DataFrame only has %d CATEGORICAL column, which is insufficient for some plots "
                "like Parallel Categories. These plots will not be displayed."
                % len(self.data_source.numerical_columns)
            )

    def _ipython_display_(self):
        from IPython.core.display import display
        from ipywidgets import widgets

        root_widget: widgets.Widget = self.layout.build()
        # noinspection PyTypeChecker
        display(root_widget)

    def _check_numerical_plots(self) -> typing.List[str]:
        numerical_plots = {"ParallelCoordinates"}
        found_plots = set()
        for row in self.layout.layout_spec:
            for el in row:
                if el in numerical_plots:
                    found_plots.add(el)
        return list(found_plots)

    def _check_categorical_plots(self) -> typing.List[str]:
        numerical_plots = {"ParallelCategories"}
        found_plots = set()
        for row in self.layout.layout_spec:
            for el in row:
                if el in numerical_plots:
                    found_plots.add(el)
        return list(found_plots)
