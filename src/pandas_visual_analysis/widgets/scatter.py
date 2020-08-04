import ipywidgets as widgets
import plotly.graph_objs as go
from traitlets import HasTraits

from pandas_visual_analysis import DataSource
from pandas_visual_analysis.utils.config import Config
from pandas_visual_analysis.widgets.base_widget import BaseWidget
from pandas_visual_analysis.widgets.registry import register_widget


@register_widget
class ScatterWidget(BaseWidget):

    def __init__(self, data_source: DataSource, row: int, index: int):
        super().__init__(data_source, row, index)

        all_columns = self.data_source.numerical_columns + \
                      self.data_source.time_columns + \
                      self.data_source.categorical_columns
        # we know that the dataframe has at least two columns so this is safe
        self.initial_x = all_columns[0]
        self.initial_y = all_columns[1]

        self.x_selection = widgets.Dropdown(
            options=self.data_source.columns,
            value=self.initial_x,
            description='x-Axis:'
        )

        self.y_selection = widgets.Dropdown(
            options=self.data_source.columns,
            value=self.initial_x,
            description='y-Axis:'
        )

        self.size_selection = widgets.Dropdown(
            options=["None"] + self.data_source.columns,
            value="None",
            description='Size:'
        )

        self.x_selection.observe(handler=self.on_axis_change, names='value')
        self.y_selection.observe(handler=self.on_axis_change, names='value')
        self.size_selection.observe(handler=self.on_axis_change, names='value')

        self.trace: go.Scattergl = self._get_scatter()

        self.figure_widget: go.FigureWidget = go.FigureWidget(data=[self.trace], layout=go.Layout(
            dragmode='lasso'
        ))
        self.figure_widget.data[0].on_selection(callback=self.on_selection)
        self.set_observers()

    def _get_scatter(self):
        config = Config()
        return go.Scattergl(x=self.data_source.data[self.x_selection.value],
                            y=self.data_source.data[self.y_selection.value],
                            opacity=config.alpha,
                            mode='markers',
                            marker={'color': 'rgb(%d,%d,%d)' % config.deselect_color},
                            selected={'marker': {'color': 'rgb(%d,%d,%d)' % config.select_color}},
                            unselected={'marker': {'opacity': config.alpha / 2}})

    def build(self):
        return widgets.VBox([self._get_controls(), self.figure_widget])

    # @observe('self.data_source._brushed_indices')
    def observe_brush_indices_change(self, change):
        # print("data_source._brushed_indices changed in Scatter(%d,%d)" % (self.row, self.index))
        new_indices = change['new']
        # noinspection SpellCheckingInspection
        self.figure_widget.data[0].selectedpoints = new_indices

    def observe_brush_data_change(self, change):
        pass

    def set_observers(self):
        HasTraits.observe(self.data_source, handler=self.observe_brush_indices_change, names='_brushed_indices')

    def on_selection(self, trace, points, state):
        # print("selection in Scatter(%d,%d)" % (self.row, self.index))
        self.data_source._brushed_indices = points.point_inds

    def on_axis_change(self, change):
        # print("axis change in Scatter(%d,%d)" % (self.row, self.index))
        self._redraw_plot()

    def _get_controls(self):
        return widgets.HBox([self.x_selection, self.y_selection, self.size_selection])

    def _redraw_plot(self):
        self.figure_widget.data[0].x = self.data_source.data[self.x_selection.value]
        self.figure_widget.data[0].y = self.data_source.data[self.y_selection.value]
        if self.size_selection.value != "None":
            self.figure_widget.data[0].marker['size'] = self.data_source.data[self.size_selection.value]
        else:
            self.figure_widget.data[0].marker['size'] = None
