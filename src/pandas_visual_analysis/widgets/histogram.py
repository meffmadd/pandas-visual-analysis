import ipywidgets as widgets
import plotly.graph_objs as go

from pandas_visual_analysis import DataSource
from pandas_visual_analysis.utils.config import Config
from pandas_visual_analysis.widgets import BaseWidget, register_widget


@register_widget
class HistogramWidget(BaseWidget):
    """

    The HistogramWidget displays a single dimension of the data as a histogram where the brush selection
    is overlaid to see the distribution of both the underlying data and the selection.
    """

    def __init__(
        self,
        data_source: DataSource,
        row: int,
        index: int,
        relative_size: float,
        max_height: int,
    ):
        """

        :param data_source: :class:`pandas_visual_analysis.data_source.DataSource` for the widget.
        :param row: The row the widget is in.
        :param index: Index of the row the widget is in.
        :param relative_size: The space the widget has in a row which is then converted to the width. (e.g. 0.33 => 33%)
        :param max_height: height in pixels the plot has to have
        """
        super().__init__(data_source, row, index, relative_size, max_height)

        self.columns = (
            data_source.numerical_columns
            + data_source.time_columns
            + data_source.categorical_columns
        )

        self.column_select = widgets.Dropdown(
            options=self.columns,
            value=self.data_source.column_store.next_prefer_numerical(),
            description="Column:",
        )
        self.normalize = widgets.Checkbox(
            value=False, description="Normalize", indent=False
        )

        self.data = self.data_source.data
        self.brushed_data = self.data_source.brushed_data

        self.figure = self._get_histograms()
        self.figure_widget = go.FigureWidget(self.figure)

        self.set_observers()
        self.column_select.observe(handler=self._on_column_change, names="value")
        self.normalize.observe(handler=self._on_normalize_change, names="value")
        self.figure_widget.data[0].on_selection(callback=self.on_selection)
        self.figure_widget.data[0].on_deselect(callback=self.on_deselection)
        self.selection_initiated = (
            True  # set to True for _redraw_plot in order to set values correctly
        )
        self._redraw_plot(
            only_brushed=True,
            selection_reset=(
                len(self.data_source.brushed_indices) == len(self.data_source)
            ),
        )
        self.selection_initiated = False

    def build(self) -> widgets.Widget:
        root = widgets.VBox(
            [widgets.HBox([self.column_select, self.normalize]), self.figure_widget]
        )
        return self.apply_size_constraints(root)

    def observe_brush_indices_change(self, sender):
        self.brushed_data = self.data_source.brushed_data
        selection_reset = len(self.brushed_data) == len(self.data)

        self._redraw_plot(selection_reset=selection_reset)

        # empty selection for histogram does not work
        if len(self.data_source.brushed_indices) == 0:
            print("ATTENTION: setting visibility of data[1] to false")
            print("brushed_indices:", self.data_source.brushed_indices)
            self.figure_widget.data[1].visible = False

        self.figure_widget.data[
            1
        ].selectedpoints = (
            self.data_source.brushed_indices
        )  # set selected points so that double click works

        self.selection_initiated = False

    def on_selection(self, trace, points, state):
        self.selection_initiated = True
        print("SELECTED POINTS:", points.point_inds)
        self.data_source.brushed_indices = points.point_inds

    def on_deselection(self, trace, points):
        self.data_source.reset_selection()

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
        fig = go.Figure(layout=go.Layout(margin=dict(l=5, r=5, b=5, t=5, pad=2)))
        fig.add_trace(
            go.Histogram(  # ALL DATA: 0
                x=self.data[col],
                opacity=max(config.alpha, 0.75),
                marker={"color": "rgb(%d,%d,%d)" % config.deselect_color},
                selected={"marker": {"color": "rgb(%d,%d,%d)" % config.deselect_color}},
                unselected={"marker": {"opacity": 0.4}},
                hoverinfo="skip",
                histnorm="",
                bingroup="1",
            )
        )
        fig.add_trace(
            go.Histogram(  # SELECTED DATA: 1
                x=self.brushed_data[col],
                opacity=1.0,
                # mode='markers',
                marker={"color": "rgb(%d,%d,%d)" % config.select_color},
                selected={"marker": {"color": "rgb(%d,%d,%d)" % config.select_color}},
                unselected={"marker": {"opacity": 1.0}},
                hoverinfo="skip",
                histnorm="",
                bingroup="1",
            )
        )
        fig.update_layout(barmode="overlay", showlegend=False, dragmode="select")
        return fig

    def _redraw_plot(self, only_brushed=True, selection_reset=False):
        col = self.column_select.value
        with self.figure_widget.batch_update():
            if not only_brushed:
                self.figure_widget.data[0].x = self.data[col]
            if self.selection_initiated or selection_reset:
                self._set_directly_selected()
                print("directly selected")
                # self.figure_widget.data[0].selectedpoints = self.data_source.brushed_indices
            else:
                self._set_externally_selected()
                print("externally selected")
                self.figure_widget.data[0].selectedpoints = self.data_source.indices
                self.figure_widget.data[1].x = self.brushed_data[col]

    def _set_directly_selected(self):
        self.figure_widget.data[0].visible = True
        self.figure_widget.data[0].marker = {
            "color": "rgb(%d,%d,%d)" % Config().select_color
        }
        self.figure_widget.data[0].unselected = {
            "marker": {
                "opacity": Config().alpha,
                "color": "rgb(%d,%d,%d)" % Config().deselect_color,
            }
        }
        self.figure_widget.data[0].selected = {
            "marker": {"color": "rgb(%d,%d,%d)" % Config().select_color}
        }
        self.figure_widget.data[0].opacity = 1.0
        self.figure_widget.data[1].visible = False

    def _set_externally_selected(self):
        self.figure_widget.data[0].visible = True
        self.figure_widget.data[0].marker = {
            "color": "rgb(%d,%d,%d)" % Config().deselect_color
        }
        self.figure_widget.data[0].unselected = {"marker": {"opacity": 0.4}}
        self.figure_widget.data[0].selected = {
            "marker": {"color": "rgb(%d,%d,%d)" % Config().deselect_color}
        }
        self.figure_widget.data[0].opacity = max(Config().alpha, 0.75)
        self.figure_widget.data[1].visible = True
