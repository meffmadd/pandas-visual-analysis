import ipywidgets as widgets
import plotly.graph_objects as go
from traitlets import HasTraits

from pandas_visual_analysis import DataSource
from pandas_visual_analysis.utils.config import Config
from pandas_visual_analysis.widgets import BaseWidget, register_widget


@register_widget
class BoxPlotWidget(BaseWidget):
    """
    The BoxPlotWidget displays a box plot for a single column with additional information of mean and standard deviation
    as a diamond.
    Per default the plot shows all the points side-by-side in order to select points.
    This behaviour can be changed to show only the outliers as points or no points at all.

    :param data_source: :class:`pandas_visual_analysis.data_source.DataSource` for the widget.
    :param row: The row the widget is in.
    :param index: Index of the row the widget is in.
    :param relative_size: The space the widget has in a row which is then converted to the width. (e.g. 0.33 => 33%)
    :param max_height: height in pixels the plot has to have
    """

    def __init__(
        self,
        data_source: DataSource,
        row: int,
        index: int,
        relative_size: float,
        max_height: int,
    ):
        super().__init__(data_source, row, index, relative_size, max_height)

        self.columns = self.data_source.numerical_columns
        if len(self.columns) < 1:
            raise ValueError(
                "The data contains too few numerical columns to display box plots. "
                "Remove the widget from the layout!"
            )

        self.column_select = widgets.Dropdown(
            options=self.columns,
            value=self.columns[0],
            description="Column:",
            style={"description_width": "60px"},
        )
        self.box_point_select = widgets.Dropdown(
            options=[("All", "all"), ("Outliers", "outliers"), ("None", False)],
            value="all",
            description="Points:",
            style={"description_width": "50px"},
        )

        self.trace, self.figure_widget = self._get_figure_widget()

        self.figure_widget.data[0].selectedpoints = self.data_source.brushed_indices
        self.figure_widget.data[0].on_selection(callback=self.on_selection)
        self.figure_widget.data[0].on_deselect(callback=self.on_deselection)
        self.column_select.observe(handler=self._on_column_change, names="value")
        self.box_point_select.observe(handler=self._on_box_point_change, names="value")
        self.set_observers()

    def build(self) -> widgets.Widget:
        root = widgets.VBox(
            [
                widgets.HBox([self.column_select, self.box_point_select]),
                self.figure_widget,
            ]
        )
        return self.apply_size_constraints(root)

    def apply_size_constraints(self, widget):
        return super().apply_size_constraints(widget)

    def observe_brush_indices_change(self, change):
        new_indices = change["new"]
        # noinspection SpellCheckingInspection
        self.figure_widget.data[0].selectedpoints = new_indices

    def set_observers(self):
        HasTraits.observe(
            self.data_source,
            handler=self.observe_brush_indices_change,
            names="_brushed_indices",
        )

    def on_selection(self, trace, points, state):
        self.data_source.brushed_indices = points.point_inds

    def on_deselection(self, trace, points):
        self.data_source.reset_selection()

    def _get_figure_widget(self):
        config = Config()
        trace = go.Box(
            y=self.data_source.data[self.column_select.value],
            boxmean="sd",
            boxpoints=self.box_point_select.value,
            jitter=0.5,
            pointpos=-1.8,
            hoverinfo="skip",
            marker={"color": "rgb(%d,%d,%d)" % config.select_color},
            selected={
                "marker": {
                    "color": "rgb(%d,%d,%d)" % config.select_color,
                    "opacity": config.alpha,
                }
            },
            unselected={
                "marker": {
                    "color": "rgb(%d,%d,%d)" % config.deselect_color,
                    "opacity": config.alpha / 2,
                }
            },
            showlegend=False,
        )

        figure_widget = go.FigureWidget(
            data=[trace],
            layout=go.Layout(
                dragmode="select",
                margin=dict(l=15, r=15, b=15, t=15, pad=2),
                xaxis=dict(zeroline=False, showticklabels=False),
            ),
        )
        return trace, figure_widget

    def _on_column_change(self, change):
        self.figure_widget.data[0].update(
            {"y": self.data_source.data[self.column_select.value]}
        )

    def _on_box_point_change(self, change):
        self.figure_widget.data[0].update({"boxpoints": self.box_point_select.value})
