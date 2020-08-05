from .data_source import DataSource
from .layout import AnalysisLayout
from .visual_analysis import VisualAnalysis


def import_widgets():
    """
    Import Widgets so that they get registered
    """
    from pandas_visual_analysis.widgets import ScatterWidget, ParallelCoordinatesWidget


import_widgets()
