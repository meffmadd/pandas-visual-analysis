from typing import List

import pandas as pd
import numpy as np
import plotly.graph_objs as go
from traitlets import HasTraits
import ipywidgets as widgets

from pandas_visual_analysis import DataSource
from pandas_visual_analysis.utils.config import Config
from pandas_visual_analysis.widgets import BaseWidget, register_widget


@register_widget
class ParallelCoordinatesWidget(BaseWidget):

    def __init__(self, data_source: DataSource, row: int, index: int):
        super().__init__(data_source, row, index)

        # todo: implement behaviour for few numerical columns (HTML message)

        self.columns: List[str] = data_source.numerical_columns
        self.many_dimensions = len(self.columns) > 10  # todo: insert multi_select if true

        self.trace: go.Parcoords = self._get_par_coords()

        self.figure_widget: go.FigureWidget = go.FigureWidget(data=[self.trace], layout=go.Layout(
            margin=dict(
                l=50,
                r=50,
                b=30,
                t=50,
                pad=10
            ),
        ))

        self.change_initiated = False

        def f(x, y):
            pass
        self.pass_func = f

        self.figure_widget.data[0].on_change(self._on_selection_helper, 'dimensions')

        self.set_observers()

    def build(self):
        return widgets.HBox([self.figure_widget], layout= widgets.Layout(width='100%'))

    def observe_brush_indices_change(self, change):
        if not self.change_initiated:
            # shortly disable selection behaviour to reset constraint ranges
            self.figure_widget.data[0].on_change(self.pass_func, 'dimensions')
            for dimension in self.figure_widget.data[0].dimensions:
                dimension['constraintrange'] = None
            self.figure_widget.data[0].on_change(self._on_selection_helper, 'dimensions')

        self.change_initiated = False

        new_indices = change['new']

        new_color = np.zeros(self.data_source.len, dtype='uint8')
        new_color[new_indices] = 1
        self.figure_widget.data[0].line.color = new_color

    def observe_brush_data_change(self, change):
        pass

    def set_observers(self):
        HasTraits.observe(self.data_source, handler=self.observe_brush_indices_change, names='_brushed_indices')

    def on_selection(self, trace, points, state):
        self.change_initiated = True

        new_color = np.zeros(self.data_source.len, dtype='uint8')
        new_color[points] = 1
        self.figure_widget.data[0].line.color = new_color

        self.data_source._brushed_indices = points

    def _on_selection_helper(self, obj, dimensions):
        constraint_ranges = {dim['label']: dim['constraintrange'] for dim in dimensions if dim['constraintrange']}
        if len(list(constraint_ranges.keys())) == 0:
            self.on_deselection(None, None)
            return
        mask = self._get_constraint_mask(constraint_ranges)
        points = list(np.arange(self.data_source.len)[mask])
        self.on_selection(None, points, None)

    def _get_constraint_mask(self, constraint_ranges: dict) -> np.array:
        cols = list(constraint_ranges.keys())
        mask: np.array = np.full(self.data_source.len, fill_value=True, dtype=bool)
        for col in cols:
            range_tuple = constraint_ranges[col]
            if all(isinstance(x, float) for x in range_tuple):
                range_tuple = (range_tuple,)
            intermediate_mask: np.array = np.full(self.data_source.len, fill_value=False, dtype=bool)
            for ranges in range_tuple:
                intermediate_mask |= (self.data_source.data[col].between(ranges[0], ranges[1])).values
            mask &= intermediate_mask
        return mask

    def on_deselection(self, trace, points):
        print("on_deselection")
        self.data_source.reset_selection()

    def _get_par_coords(self) -> go.Parcoords:
        config = Config()

        self.trace: go.Parcoords = go.Parcoords(
            line=dict(color=config.color_scale[1][1], colorscale=config.color_scale, cmin=0, cmax=1),
            dimensions=[self._get_dimension_dict(col) for col in self.columns]
        )

        return self.trace

    def _get_dimension_dict(self, col: str) -> dict:
        series: pd.Series = self.data_source.data[col]
        return dict(
            range=[series.min(), series.max()],
            label=col,
            values=series
        )

