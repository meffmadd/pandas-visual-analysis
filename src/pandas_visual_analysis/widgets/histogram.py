import ipywidgets as widgets

from pandas_visual_analysis import DataSource
from pandas_visual_analysis.widgets import BaseWidget


class HistogramWidget(BaseWidget):
    def __init__(self, data_source: DataSource, row: int, index: int, relative_size: float, max_height: int):
        super().__init__(data_source, row, index, relative_size, max_height)

    def build(self) -> widgets.Widget:
        pass

    def observe_brush_indices_change(self, change):
        pass

    def set_observers(self):
        pass

    def on_selection(self, trace, points, state):
        pass

    def on_deselection(self, trace, points):
        pass
