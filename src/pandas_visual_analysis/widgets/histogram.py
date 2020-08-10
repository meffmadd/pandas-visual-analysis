import ipywidgets as widgets
import plotly.graph_objs as go
from traitlets import HasTraits

from pandas_visual_analysis import DataSource
from pandas_visual_analysis.utils.config import Config
from pandas_visual_analysis.widgets import BaseWidget, register_widget


@register_widget
class HistogramWidget(BaseWidget):
    def __init__(self, data_source: DataSource, row: int, index: int, relative_size: float, max_height: int):
        super().__init__(data_source, row, index, relative_size, max_height)

        self.columns = data_source.numerical_columns + data_source.time_columns + data_source.categorical_columns

        self.column_select = widgets.Dropdown(options=self.columns, value=self.columns[0], description="Column:")
        self.normalize = widgets.Checkbox(value=False, description='Normalize', indent=False)

        self.data = self.data_source.data
        self.brushed_data = self.data_source.brushed_data

        self.figure_widget = self._get_figure_widget()

        self.set_observers()
        self.column_select.observe(handler=self._on_column_change, names='value')
        self.normalize.observe(handler=self._on_normalize_change, names='value')

    def build(self) -> widgets.Widget:
        root = widgets.VBox([widgets.HBox([self.column_select, self.normalize]), self.figure_widget])
        return self.apply_size_constraints(root)

    def observe_brush_indices_change(self, change):
        self.brushed_data = self.data_source.brushed_data
        if len(self.brushed_data) == len(self.data):
            self.figure_widget.data[0].visible = False
        else:
            self.figure_widget.data[0].visible = True

        self._redraw_plot()

    def set_observers(self):
        HasTraits.observe(self.data_source, handler=self.observe_brush_indices_change, names='_brushed_indices')

    # issue: selection does not work for histogram: https://github.com/plotly/plotly.py/issues/2698
    def on_selection(self, trace, points, state):
        pass

    def on_deselection(self, trace, points):
        pass

    def _on_column_change(self, change):
        self._redraw_plot(only_brushed=False)

    def _on_normalize_change(self, change):
        use_norm = self.normalize.value
        hist_norm = "probability" if use_norm else ""
        with self.figure_widget.batch_update():
            self.figure_widget.data[0].histnorm = hist_norm
            self.figure_widget.data[1].histnorm = hist_norm

    def _get_figure_widget(self):
        return go.FigureWidget(self._get_histograms())

    def _get_histograms(self):
        col = self.column_select.value
        config = Config()
        fig = go.Figure(layout=go.Layout(margin=dict(
                                   l=5,
                                   r=5,
                                   b=5,
                                   t=5,
                                   pad=2
                               )))
        fig.add_trace(go.Histogram(x=self.data[col],
                                   opacity=max(config.alpha, 0.75),
                                   marker={'color': 'rgb(%d,%d,%d)' % config.deselect_color},
                                   selected={'marker': {'color': 'rgb(%d,%d,%d)' % config.select_color}},
                                   unselected={'marker': {'opacity': 0.5}},
                                   hoverinfo='skip', histnorm=''))
        fig.add_trace(go.Histogram(x=self.brushed_data[col],
                                   opacity=1.0,
                                   # mode='markers',
                                   marker={'color': 'rgb(%d,%d,%d)' % config.select_color},
                                   selected={'marker': {'color': 'rgb(%d,%d,%d)' % config.select_color}},
                                   unselected={'marker': {'opacity': 1.0}},
                                   hoverinfo='skip', histnorm=''))
        fig.update_layout(barmode='overlay', showlegend=False)
        return fig

    def _redraw_plot(self, only_brushed=True):
        col = self.column_select.value
        with self.figure_widget.batch_update():
            self.figure_widget.data[1].x = self.brushed_data[col]
            if not only_brushed:
                self.figure_widget.data[0].x = self.data[col]
