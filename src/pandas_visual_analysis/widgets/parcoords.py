import numbers

import ipywidgets as widgets
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from traitlets import HasTraits

from pandas_visual_analysis import DataSource
from pandas_visual_analysis.utils.config import Config
from pandas_visual_analysis.widgets import BaseWidget, register_widget
from pandas_visual_analysis.widgets.helpers.multi_select import (
    HasMultiSelect,
)


@register_widget
class ParallelCoordinatesWidget(BaseWidget, HasMultiSelect):
    """
    The ParallelCoordinatesWidget shows a parallel coordinates plot for high dimensional data and supports brushing.
    Only displays numerical columns, which can be reordered arbitrarily.
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
        super(ParallelCoordinatesWidget, self).__init__(
            data_source, row, index, relative_size, max_height
        )
        super(BaseWidget, self).__init__(
            self.data_source.numerical_columns, relative_size, max_height
        )
        if len(self.columns) < 1:
            raise ValueError(
                "The data contains too few numerical columns to display a parallel coordinates plot."
                "Remove the widget from the layout!"
            )

        if self.use_multi_select:
            self.multi_select_toggle: widgets.Button = widgets.Button(
                description="Hide Selection"
            )
            # self.multi_select_toggle.on_click(callback=self._toggle_multi_select)

        self.trace, self.figure_widget = self._get_figure_widget()
        self.constraint_ranges = {}

        self.change_initiated = False

        def f(x, y):
            pass

        self.pass_func = f

        self.set_observers()

        # set root here because need to toggle the select and need widgets for that
        self.root: widgets.Widget = widgets.HBox(
            [self.figure_widget], layout=widgets.Layout(width="100%")
        )
        if self.multi_select:
            self.root = widgets.HBox([self.figure_widget, self.multi_select_widget])
        if self.data_source.few_num_cols:
            pass  # todo: implement behaviour for few numerical columns (HTML message)

    def build(self):
        return self.apply_size_constraints(self.root)

    def observe_brush_indices_change(self, change):
        if not self.change_initiated:
            # shortly disable selection behaviour to reset constraint ranges
            self.figure_widget.data[0].on_change(self.pass_func, "dimensions")
            with self.figure_widget.batch_update(), self.figure_widget.hold_trait_notifications():
                for dimension in self.figure_widget.data[0].dimensions:
                    dimension["constraintrange"] = None
            self.figure_widget.data[0].on_change(
                self._on_selection_helper, "dimensions"
            )
            self.constraint_ranges = {}

        self.change_initiated = False

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
        self.change_initiated = True

        new_color = np.zeros(self.data_source.len, dtype="uint8")
        new_color[points] = 1
        with self.figure_widget.batch_update(), self.figure_widget.hold_trait_notifications():
            self.figure_widget.data[0].line.color = new_color

        self.data_source.brushed_indices = points

    def _on_selection_helper(self, obj, dimensions):
        old_ranges = self.constraint_ranges
        self.constraint_ranges = {
            dim["label"]: dim["constraintrange"]
            for dim in dimensions
            if dim["constraintrange"]
        }
        if self.constraint_ranges == old_ranges:
            return  # this is the case when the user just reorders the dimensions
        if len(list(self.constraint_ranges.keys())) == 0:
            self.on_deselection(None, None)
            return
        mask = self._get_constraint_mask(self.constraint_ranges)
        points = list(np.arange(self.data_source.len)[mask])
        self.on_selection(None, points, None)

    def _get_constraint_mask(self, constraint_ranges: dict) -> np.array:
        cols = list(constraint_ranges.keys())
        mask: np.array = np.full(self.data_source.len, fill_value=True, dtype=bool)
        for col in cols:
            range_tuple = constraint_ranges[col]
            if all(isinstance(x, numbers.Number) for x in range_tuple):
                range_tuple = (range_tuple,)
            intermediate_mask: np.array = np.full(
                self.data_source.len, fill_value=False, dtype=bool
            )
            for ranges in range_tuple:
                intermediate_mask |= (
                    self.data_source.data[col].between(ranges[0], ranges[1])
                ).values
            mask &= intermediate_mask
        return mask

    def on_deselection(self, trace, points):
        self.data_source.reset_selection()

    def _get_par_coords(self) -> go.Parcoords:
        config = Config()

        self.trace: go.Parcoords = go.Parcoords(
            line=dict(
                color=config.color_scale[1][1],
                colorscale=config.color_scale,
                cmin=0,
                cmax=1,
            ),
            dimensions=[self._get_dimension_dict(col) for col in self.selected_columns],
        )
        return self.trace

    def _get_figure_widget(self):
        trace: go.Parcoords = self._get_par_coords()
        figure_widget: go.FigureWidget = go.FigureWidget(
            data=[self.trace],
            layout=go.Layout(
                margin=dict(l=50, r=50, b=30, t=50, pad=10),
                autosize=True,
                xaxis=dict(automargin=True),
                showlegend=False,
            ),
        )
        figure_widget.data[0].on_change(self._on_selection_helper, "dimensions")

        return trace, figure_widget

    def _get_dimension_dict(self, col: str) -> dict:
        series: pd.Series = self.data_source.data[col]
        return dict(range=[series.min(), series.max()], label=col, values=series)

    # def _toggle_multi_select(self, obj):
    #     if self.multi_select:
    #         self.show_multi_select = not self.show_multi_select
    #         button_description = "Hide" if self.show_multi_select else "Show"
    #         self.multi_select_toggle.description = button_description + " Selection"
    #
    #         if self.show_multi_select:
    #             children = (self.figure_widget, self.multi_select_widget)
    #         else:
    #             children = (self.figure_widget,)
    #         self.root.children = (self.multi_select_toggle, widgets.HBox(children))

    def _on_selected_columns_changed(self, change):
        self.selected_columns = change["new"]
        self._redraw_plot()

    def _redraw_plot(self):
        # shortly disable selection behaviour to reset constraint ranges
        self.figure_widget.data[0].on_change(self.pass_func, "dimensions")

        old_constraint_ranges = {
            dim["label"]: dim["constraintrange"]
            for dim in self.figure_widget.data[0].dimensions
            if dim["constraintrange"]
        }
        with self.figure_widget.batch_update(), self.figure_widget.hold_trait_notifications():
            self.figure_widget.data[0].dimensions = [
                self._get_dimension_dict(col) for col in self.selected_columns
            ]
            for dim in self.figure_widget.data[0].dimensions:
                if dim["label"] in old_constraint_ranges.keys():
                    dim["constraintrange"] = old_constraint_ranges[dim["label"]]

        self.figure_widget.data[0].on_change(self._on_selection_helper, "dimensions")
