import typing
import warnings

from pandas import DataFrame
from traitlets import HasTraits, Instance, Tuple, Int, Float, TraitError, validate

from pandas_visual_analysis.data_source import DataSource
from pandas_visual_analysis.layout import AnalysisLayout
from pandas_visual_analysis.utils.config import Config
from pandas_visual_analysis.utils.util import hex_to_rgb


class VisualAnalysis:
    """
    Generate linked plots that support brushing from a pandas.DataFrame and display them in Jupyter notebooks.

    :param df: the pandas.DataFrame object
    :param categorical_columns: if given, specifies which columns are to be interpreted as categorical
    :param layout: layout specification name or explicit definition of plot in rows
    :param sample: int or float specifying if the DataFrame should be sub-sampled.
        When an int is given, the DataFrame will be limited to that number of rows given by the value.
        When a float is given, the DataFrame will include the fraction of rows given by the value.
    :param select_color: RGB tuple or hex color specifying the color display selected data points
    :param deselect_color: RGB tuple or hex color specifying the color display deselected data points
    :param alpha: opacity of data points
    """

    def __init__(self, df: DataFrame, categorical_columns: typing.Union[typing.List[str], None] = None,
                 layout: typing.Union[str, typing.List[typing.List[str]]] = 'default',
                 sample: typing.Union[float, int, None] = None,
                 select_color: typing.Union[str, typing.Tuple[int, int, int]] = '#323EEC',
                 deselect_color: typing.Union[str, typing.Tuple[int, int, int]] = '#8A8C93',
                 alpha: float = 0.75
                 ):
        super().__init__()

        if not isinstance(alpha, float) or isinstance(alpha, int):
            raise TypeError("Alpha has to be a floating point value, not %s", str(type(alpha)))
        if alpha < 0.0 or alpha > 1.0:
            raise ValueError("Alpha value has to be between 0.0 and 1.0. Invalid value: %d" % alpha)

        if sample is None:
            self.df = df
        else:
            if isinstance(sample, float):
                if sample < 0.0 or sample > 1.0:
                    raise ValueError("Sample has to be between 0.0 and 1.0. Invalid value : %d" % sample)
                self.df = df.sample(frac=sample)
            else:
                if sample < 0 or sample > len(df):
                    raise ValueError("Sample has to be between 0 and the length of the DataFrame (%d). Invalid value: "
                                     "%d" % (len(df), sample))
                self.df = df.sample(n=sample)

        if isinstance(select_color, str):
            self.select_color = hex_to_rgb(select_color)
        elif isinstance(select_color, tuple):
            if len(select_color) != 3:
                raise ValueError("The tuple specifying select_color has to be of length 3.")
            self.select_color = select_color
        else:
            raise TypeError("The type of select_color has to be a string or tuple.")

        if isinstance(deselect_color, str):
            self.deselect_color = hex_to_rgb(deselect_color)
        elif isinstance(deselect_color, tuple):
            if len(deselect_color) != 3:
                raise ValueError("The tuple specifying deselect_color has to be of length 3.")
            self.deselect_color = deselect_color
        else:
            raise TypeError("The type of deselect_color has to be a string or tuple.")

        if not (0 <= self.select_color[0] <= 255) \
                or not (0 <= self.select_color[1] <= 255) \
                or not (0 <= self.select_color[2] <= 255):
            raise ValueError("RGB values have to be between 0 and 255. Invalid values: %s" % str(self.select_color))

        if not (0 <= self.deselect_color[0] <= 255) \
                or not (0 <= self.deselect_color[1] <= 255) \
                or not (0 <= self.deselect_color[2] <= 255):
            raise ValueError("RGB values have to be between 0 and 255. Invalid values: %s" % str(self.deselect_color))

        self.alpha = alpha
        self.color_scale = [[0, 'rgb(%d,%d,%d)' % self.deselect_color], [1, 'rgb(%d,%d,%d)' % self.select_color]]

        config = Config()
        config['alpha'] = self.alpha
        config['select_color'] = self.select_color
        config['deselect_color'] = self.deselect_color
        config['color_scale'] = self.color_scale

        self.data_source = DataSource(df=df, categorical_columns=categorical_columns)
        self.layout = AnalysisLayout(layout=layout, data_source=self.data_source)

        if self.data_source.few_num_cols and len(self._check_numerical_plots()) != 0:
            warnings.warn("The passed DataFrame only has %d NUMERICAL column, which is insufficient for some plots "
                          "like Parallel Coordinates. These plots will not be displayed."
                          % len(self.data_source.numerical_columns))

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


