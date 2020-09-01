import pytest
import ipywidgets as widgets

from pandas_visual_analysis import DataSource
from pandas_visual_analysis.utils.config import Config
from pandas_visual_analysis.widgets import BoxPlotWidget
from tests import sample_dataframes


@pytest.fixture(scope="module")
def small_df():
    return sample_dataframes.small_df()


@pytest.fixture(scope="module")
def populated_config():
    config = Config()
    config.alpha = 0.75
    config.select_color = (0, 0, 0)
    config.deselect_color = (0, 0, 0)
    config.color_scale = [
        [0, "rgb(%d,%d,%d)" % config.deselect_color],
        [1, "rgb(%d,%d,%d)" % config.select_color],
    ]


class PointsObject:
    def __init__(self, indices):
        self.point_inds = indices


class TestInit:
    def test_object_creation(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        BoxPlotWidget(ds, 0, 0, 1.0, 400)

    def test_normal_few_cols_html(self, small_df, populated_config):
        df = small_df.drop(columns=["a", "c"])
        ds = DataSource(df, None)
        with pytest.raises(ValueError):
            BoxPlotWidget(ds, 0, 0, 1.0, 400)


class TestBuild:
    def test_normal_build(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        bp = BoxPlotWidget(ds, 0, 0, 1.0, 400)
        root_widget = bp.build()
        assert isinstance(root_widget, widgets.VBox)


class TestOnSelection:
    def test_on_selection(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        bp = BoxPlotWidget(ds, 0, 0, 1.0, 400)

        points = PointsObject([1, 2, 3])
        bp.on_selection(None, points, None)

        assert ds.brushed_indices == set(points.point_inds)

    def test_on_deselection(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        ds.brushed_indices = [0]
        bp = BoxPlotWidget(ds, 0, 0, 1.0, 400)
        bp.on_deselection(None, None)
        assert len(ds.brushed_indices) == len(small_df)


class TestBrushIndicesChange:
    def test_brush_indices_change(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        bp = BoxPlotWidget(ds, 0, 0, 1.0, 400)
        bp.build()
        ds.brushed_indices = [1, 2, 3]

        assert bp.figure_widget.data[0].selectedpoints == ds.brushed_indices

    def test_brush_indices_change_deselect(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        ds.brushed_indices = [1, 2, 3]
        bp = BoxPlotWidget(ds, 0, 0, 1.0, 400)
        bp.build()
        ds.reset_selection()

        assert bp.figure_widget.data[0].selectedpoints == ds.indices


class TestSelectUI:
    def test_column_select(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        bp = BoxPlotWidget(ds, 0, 0, 1.0, 400)
        bp.column_select.value = "c"
        assert list(bp.figure_widget.data[0].y) == list(small_df["c"].values)

    def test_box_points(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        bp = BoxPlotWidget(ds, 0, 0, 1.0, 400)
        bp.box_point_select.value = "outliers"

        assert bp.figure_widget.data[0].boxpoints == "outliers"
