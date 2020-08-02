import warnings

from traitlets import HasTraits, Instance, Tuple, Int, Float, TraitError, validate
from traitlets.config import Config
from pandas import DataFrame
import typing

from pandas_visual_analysis.data_source import DataSource
from pandas_visual_analysis.layout import AnalysisLayout
from tests import sample_dataframes
from pandas_visual_analysis.utils.util import hex_to_rgb


class VisualAnalysis(HasTraits):
    df = Instance(klass=DataFrame)
    layout = Instance(klass=AnalysisLayout)
    data_source = Instance(klass=DataSource)

    select_color = Tuple(Int(), Int(), Int())
    deselect_color = Tuple(Int(), Int(), Int())
    alpha = Float()

    def __init__(self, df: DataFrame, categorical_columns: typing.Union[typing.List[str], None] = None,
                 layout: typing.Union[str, typing.List[typing.List[str]]] = 'default',
                 sample: typing.Union[float, int, None] = None,
                 select_color: typing.Union[str, typing.Tuple[int, int, int]] = '#323EEC',
                 deselect_color: typing.Union[str, typing.Tuple[int, int, int]] = '#8A8C93',
                 alpha: float = 0.75,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        else:
            self.select_color = select_color

        if isinstance(deselect_color, str):
            self.deselect_color = hex_to_rgb(deselect_color)
        else:
            self.deselect_color = deselect_color

        self.alpha = alpha
        self.color_scale = [[0, 'rgb(%d,%d,%d)' % self.deselect_color], [1, 'rgb(%d,%d,%d)' % self.select_color]]

        config = Config()
        config['alpha'] = self.alpha
        config['select_color'] = self.select_color
        config['deselect_color'] = self.deselect_color
        config['color_scale'] = self.color_scale

        self.data_source = DataSource(df=df, categorical_columns=categorical_columns)
        self.layout = AnalysisLayout(layout=layout, data_source=self.data_source)

        if len(self.data_source.columns) < 2:
            raise ValueError("The passed DataFrame only has %d column, which is insufficient for analysis." %
                             len(self.data_source.columns))

        if len(self.data_source.numerical_columns) < 2:
            if len(self._check_numerical_plots()) != 0:
                warnings.warn("The passed DataFrame only has %d NUMERICAL column, which is insufficient for some plots "
                              "like Parallel Coordinates. These plots will not be displayed."
                              % len(self.data_source.numerical_columns))
            self.few_num_cols = True
        else:
            self.few_num_cols = False

    @validate('alpha')
    def _validate_alpha(self, proposal):
        value = proposal['value']
        if value < 0.0 or value > 1.0:
            raise TraitError("Value has to be between 0.0 and 1.0. Invalid value: %d" % value)
        return value

    @validate('select_color', 'deselect_color')
    def _validate_color(self, proposal):
        value: typing.Tuple = proposal['value']
        if not (0 <= value[0] <= 255) or not (0 <= value[1] <= 255) or not (0 <= value[2] <= 255):
            raise TraitError("RGB values have to be between 0 and 255. Invalid values: %s" % str(value))
        return value

    def _check_numerical_plots(self) -> typing.List[str]:
        numerical_plots = {"ParallelCoordinates"}
        found_plots = set()
        for row in self.layout.layout_spec:
            for el in row:
                if el in numerical_plots:
                    found_plots.add(el)
        return list(found_plots)


if __name__ == '__main__':
    small_df = sample_dataframes.small_df()
    VisualAnalysis(small_df)
