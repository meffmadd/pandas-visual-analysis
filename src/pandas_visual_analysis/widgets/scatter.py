import ipywidgets as widgets
import plotly.graph_objs as go
from traitlets.config import Config

from pandas_visual_analysis import DataSource
from pandas_visual_analysis.widgets.base_widget import BaseWidget
from pandas_visual_analysis.widgets.registry import register_widget


@register_widget
class ScatterWidget(BaseWidget):

    def __init__(self, data_source: DataSource, row: int, index: int):
        super(ScatterWidget, self).__init__(data_source, row, index)

        all_columns = self.data_source.numerical_columns + \
                      self.data_source.time_columns + \
                      self.data_source.categorical_columns
        # we know that the dataframe has at least two columns so this is safe
        self.initial_x = all_columns[0]
        self.initial_y = all_columns[1]

        self.x_selection = widgets.Dropdown(
            options=self.data_source.columns,
            value=self.initial_x,
            description='x-Value:'
        )

        self.y_selection = widgets.Dropdown(
            options=self.data_source.columns,
            value=self.initial_x,
            description='y-Value:'
        )

        self.size_selection = widgets.Dropdown(
            options=["None"] + self.data_source.columns,
            value="None",
            description='Size:'
        )

        self.trace = self._get_scatter()

        self.figure_widget = go.FigureWidget(data=[self.trace], layout=go.Layout(
            title=dict(
                text='Scatter'
            )
        ))

    def _get_scatter(self):
        config = Config()
        return go.Scattergl(x=self.data_source.data[self.x_selection.value],
                            y=self.data_source.data[self.y_selection.value],
                            opacity=self.alpha,
                            mode='markers',
                            marker={'color': 'rgb(%d,%d,%d)' % config.deselect_color},
                            selected={'marker': {'color': 'rgb(%d,%d,%d)' % config.select_color}},
                            unselected={'marker': {'opacity': config.alpha / 2}})

    def build(self):
        return widgets.VBox([self._get_controls(), self.figure_widget])

    def observe_brush_indices_change(self, change):
        pass

    def observe_brush_data_change(self, change):
        pass

    def _get_controls(self):
        return widgets.HBox([self.x_selection, self.y_selection, self.size_selection])

    def _redraw_plot(self):
        self.figure_widget.data = [self._get_scatter()]
