import ipywidgets as widgets
import plotly.graph_objects as go
import numpy as np
from traitlets import HasTraits

from pandas_visual_analysis import DataSource
from pandas_visual_analysis.utils.config import Config
from pandas_visual_analysis.widgets import BaseWidget, register_widget
from pandas_visual_analysis.widgets.helpers.multi_select import HasMultiSelect


@register_widget
class ParallelCategoriesWidget(BaseWidget, HasMultiSelect):
    """
    The ParallelCategoriesWidget is useful for high dimensional data and supports brushing.
    Only displays categorical columns, which can be reordered arbitrarily.
    Displays a multi column selection if there are too many columns to display them all at once.

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
        super(ParallelCategoriesWidget, self).__init__(
            data_source, row, index, relative_size, max_height
        )
        super(BaseWidget, self).__init__(
            self.data_source.categorical_columns, relative_size, max_height
        )
        if len(self.columns) < 1:
            raise ValueError(
                "The data contains too few categorical columns to display a parallel categories plot."
                "Remove the widget from the layout!"
            )

        self.trace, self.figure_widget = self._get_figure_widget()
        self.set_observers()

        self.root: widgets.Widget = widgets.HBox(
            [self.figure_widget], layout=widgets.Layout(width="100%")
        )
        if self.multi_select:
            self.root = widgets.HBox([self.figure_widget, self.multi_select_widget])
        if self.data_source.few_num_cols:
            pass  # todo: implement behaviour for few numerical columns (HTML message)

    def build(self) -> widgets.Widget:
        return self.apply_size_constraints(self.root)

    def apply_size_constraints(self, widget):
        return super().apply_size_constraints(widget)

    def observe_brush_indices_change(self, change):
        new_indices = change["new"]

        new_color = np.zeros(self.data_source.len, dtype="uint8")
        new_color[new_indices] = 1
        with self.figure_widget.batch_update(), self.figure_widget.hold_trait_notifications():
            self.figure_widget.data[0].line.color = new_color

    def set_observers(self):
        HasTraits.observe(
            self.data_source,
            handler=self.observe_brush_indices_change,
            names="_brushed_indices",
        )
        if self.use_multi_select:
            HasTraits.observe(
                self.multi_select,
                self._on_selected_columns_changed,
                names="selected_options",
            )

    def on_selection(self, trace, points, state):
        new_color = np.zeros(self.data_source.len, dtype="uint8")
        new_color[points.point_inds] = 1
        with self.figure_widget.batch_update(), self.figure_widget.hold_trait_notifications():
            self.figure_widget.data[0].line.color = new_color

        self.data_source.brushed_indices = points.point_inds

    def on_deselection(self, trace, points):
        pass

    def _get_figure_widget(self):
        config = Config()
        trace = go.Parcats(
            dimensions=[
                {"label": col, "values": self.data_source.data[col]}
                for col in self.selected_columns
            ],
            line=dict(
                color=config.color_scale[1][1],
                colorscale=config.color_scale,
                cmin=0,
                cmax=1,
                shape="hspline",
            ),
        )

        figure_widget = go.FigureWidget(
            data=[trace],
            layout=go.Layout(
                margin=dict(l=20, r=20, b=20, t=20, pad=5),
                autosize=True,
                showlegend=False,
            ),
        )

        figure_widget.data[0].on_click(self.on_selection)
        return trace, figure_widget

    def _on_selected_columns_changed(self, change):
        self.selected_columns = change["new"]
        self._redraw_plot()

    def _redraw_plot(self):
        new_dims = [
            {"label": col, "values": self.data_source.data[col]}
            for col in self.selected_columns
        ]
        self.figure_widget.data[0].dimensions = new_dims
        new_color = np.zeros(self.data_source.len, dtype="uint8")
        new_color[self.data_source.brushed_indices] = 1
        with self.figure_widget.batch_update(), self.figure_widget.hold_trait_notifications():
            self.figure_widget.data[0].line.color = new_color
