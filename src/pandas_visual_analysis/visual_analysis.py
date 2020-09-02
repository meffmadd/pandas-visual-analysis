import typing
import warnings

from pandas import DataFrame

from pandas_visual_analysis.data_source import DataSource
from pandas_visual_analysis.layout import AnalysisLayout
from pandas_visual_analysis.utils.config import Config
from pandas_visual_analysis.utils.util import hex_to_rgb
import pandas_visual_analysis.utils.validation as validate
from pandas_visual_analysis.widgets import WidgetClassRegistry


class VisualAnalysis:

    """
    Generate plots that support linked-brushing from a pandas `DataFrame` and display them in Jupyter notebooks.
    """

    def __init__(
        self,
        data: typing.Union[DataFrame, DataSource],
        layout: typing.Union[str, typing.List[typing.List[str]]] = "default",
        categorical_columns: typing.Union[typing.List[str], None] = None,
        row_height: typing.Union[int, typing.List[int]] = 400,
        sample: typing.Union[float, int, None] = None,
        select_color: typing.Union[str, typing.Tuple[int, int, int]] = "#323EEC",
        deselect_color: typing.Union[str, typing.Tuple[int, int, int]] = "#8A8C93",
        alpha: float = 0.75,
        seed: typing.Union[int, None] = None,
    ):
        """

        :param data: A pandas.DataFrame object or a :class:`DataSource`.
        :param layout: Layout specification name or explicit definition of widget names in rows.
            Those columns have to include all columns of the DataFrame
            which have type `object`, `str`, `bool` or `category`.
            This means it can only add columns which do not have the aforementioned types.
            Defaults to 'default'.
        :param categorical_columns: If given, specifies which columns are to be interpreted as categorical.
            Defaults to None.
        :param row_height: Height in pixels each row should have. If given an integer, each row has the height
            specified by that value, if given a list of integers, each value in the list specifies the height of
            the corresponding row.
            Defaults to 400.
        :param sample: Int or float value specifying if the DataFrame should be sub-sampled.
            When an int is given, the DataFrame will be limited to that number of rows given by the value.
            When a float is given, the DataFrame will include the fraction of rows given by the value.
            Defaults to None.
        :param select_color: RGB tuple or hex color specifying the color display selected data points.
            Values in the tuple have to be between 0 and 255 inclusive or a hex string that converts to
            such RGB values.
            Defaults to '#323EEC'.
        :param deselect_color: RGB tuple or hex color specifying the color display deselected data points.
            Values in the tuple have to be between 0 and 255 inclusive or a hex string that converts to
            such RGB values.
            Defaults to '#8A8C93'.
        :param alpha: Opacity of data points when applicable ranging from 0.0 to 1.0 inclusive. Defaults to 0.75.
        :param seed: Random seed used for sampling the data.
            Values can be any integer between 0 and 2**32 - 1 inclusive or None.
            Defaults to None.
        """
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
                df=data,
                categorical_columns=categorical_columns,
                sample=sample,
                seed=seed,
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
        """
        Builds the layout and calls :func:`IPython.core.display.display`

        :return:
        """
        from IPython.core.display import display
        from ipywidgets import widgets

        root_widget: widgets.Widget = self.layout.build()
        # noinspection PyTypeChecker
        display(root_widget)

    def _check_numerical_plots(self) -> typing.List[str]:
        """
        Checks if the layout contains widgets that can only display numerical data.

        :return: Set of widgets in the layout that are strictly numerical. Empty set otherwise.
        """
        numerical_plots = {"ParallelCoordinates"}
        found_plots = set()
        for row in self.layout.layout_spec:
            for el in row:
                if el in numerical_plots:
                    found_plots.add(el)
        return list(found_plots)

    def _check_categorical_plots(self) -> typing.List[str]:
        """
        Checks if the layout contains widgets that can only display categorical data.

        :return: Set of widgets in the layout that are strictly categorical. Empty set otherwise.
        """
        numerical_plots = {"ParallelCategories"}
        found_plots = set()
        for row in self.layout.layout_spec:
            for el in row:
                if el in numerical_plots:
                    found_plots.add(el)
        return list(found_plots)

    @staticmethod
    def widgets():
        """

        :return: All the widget names that are available as input to a layout.
        """
        return WidgetClassRegistry().widget_list
