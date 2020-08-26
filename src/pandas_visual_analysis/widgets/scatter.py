import ipywidgets as widgets
import plotly.graph_objs as go
from traitlets import HasTraits

from pandas_visual_analysis import DataSource
from pandas_visual_analysis.utils.config import Config
from pandas_visual_analysis.widgets.base_widget import BaseWidget
from pandas_visual_analysis.widgets.registry import register_widget


@register_widget
class ScatterWidget(BaseWidget):
    """
    The ScatterWidget displays a scatter plot to highlight the relation
    between two numerical, time-based or categorical dimensions.
    In addition to selecting the x- and y-axis, it is also possible show an additional dimension as the size.

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

        all_columns = (
            self.data_source.numerical_columns
            + self.data_source.time_columns
            + self.data_source.categorical_columns
        )
        # we know that the dataframe has at least two columns so this is safe
        self.initial_x = all_columns[0]
        self.initial_y = all_columns[1]

        self.x_selection = widgets.Dropdown(
            options=self.data_source.columns,
            value=self.initial_x,
            description="x:",
            style={"description_width": "20px"},
        )

        self.y_selection = widgets.Dropdown(
            options=self.data_source.columns,
            value=self.initial_y,
            description="y:",
            style={"description_width": "20px"},
        )

        self.size_selection = widgets.Dropdown(
            options=["None"] + self.data_source.numerical_columns,
            value="None",
            description="Size:",
            style={"description_width": "40px"},
        )

        self.x_selection.observe(handler=self.on_axis_change, names="value")
        self.y_selection.observe(handler=self.on_axis_change, names="value")
        self.size_selection.observe(handler=self.on_axis_change, names="value")

        self.trace: go.Scatter = self._get_scatter()

        self.figure_widget: go.FigureWidget = go.FigureWidget(
            data=[self.trace],
            layout=go.Layout(
                dragmode="lasso",
                margin=dict(l=7, r=7, b=7, t=7, pad=5),
            ),
        )
        self.figure_widget.data[0].on_selection(callback=self.on_selection)
        self.figure_widget.data[0].on_deselect(callback=self.on_deselection)
        self.set_observers()
        # initially set brush to state of data_source (for start-up where everything is deselected by default)
        self.observe_brush_indices_change(
            change={"new": self.data_source.brushed_indices}
        )

    def _get_scatter(self):
        config = Config()
        return go.Scatter(
            x=self.data_source.data[self.x_selection.value],
            y=self.data_source.data[self.y_selection.value],
            opacity=config.alpha,
            mode="markers",
            marker={"color": "rgb(%d,%d,%d)" % config.deselect_color},
            selected={"marker": {"color": "rgb(%d,%d,%d)" % config.select_color}},
            unselected={"marker": {"opacity": config.alpha / 2}},
            showlegend=False,
        )

    def build(self):
        root = widgets.VBox([self._get_controls(), self.figure_widget])
        return self.apply_size_constraints(root)

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
        # print("selection in Scatter(%d,%d)" % (self.row, self.index))
        self.data_source.brushed_indices = points.point_inds

    def on_deselection(self, trace, points):
        self.data_source.reset_selection()

    def on_axis_change(self, change):
        description = change["owner"].description.replace(":", "")
        self._redraw_plot(axis=[description.lower()])

    def _get_controls(self):
        return widgets.HBox(
            [self.x_selection, self.y_selection, self.size_selection],
            layout=widgets.Layout(max_width="100%"),
        )

    def _redraw_plot(self, axis=None):
        if axis is None:  # fix warning: default argument is mutable
            axis = ["x", "y", "size"]
        with self.figure_widget.batch_update():
            if "x" in axis:
                self.figure_widget.data[0].x = self.data_source.data[
                    self.x_selection.value
                ]
            if "y" in axis:
                self.figure_widget.data[0].y = self.data_source.data[
                    self.y_selection.value
                ]
            if "size" in axis:
                if self.size_selection.value != "None":
                    self.figure_widget.data[0].marker["size"] = self.data_source.data[
                        self.size_selection.value
                    ]
                else:
                    self.figure_widget.data[0].marker["size"] = None
