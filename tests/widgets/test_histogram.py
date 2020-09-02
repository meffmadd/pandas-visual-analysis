import pytest
import ipywidgets as widgets

from pandas_visual_analysis import DataSource
from pandas_visual_analysis.utils.config import Config
from pandas_visual_analysis.widgets import HistogramWidget
from tests import sample_dataframes


@pytest.fixture(scope="module")
def small_df():
    return sample_dataframes.small_df()


@pytest.fixture(scope="module")
def rand_cat_df():
    return sample_dataframes.random_cat_df(1000, 10)


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
        HistogramWidget(ds, 0, 0, 1.0, 400)


class TestBuild:
    def test_normal_build(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        hw = HistogramWidget(ds, 0, 0, 1.0, 400)
        root_widget = hw.build()
        assert isinstance(root_widget, widgets.VBox)


class TestOnSelection:

    # todo: update when histogram supports selection
    def test_on_selection(self, small_df, populated_config):
        pass

    def test_on_deselection(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        ds.brushed_indices = [0]
        hw = HistogramWidget(ds, 0, 0, 1.0, 400)
        hw.on_deselection(None, None)
        assert len(ds.brushed_indices) == len(small_df)


class TestBrushIndicesChange:
    def test_brush_indices_change(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        hw = HistogramWidget(ds, 0, 0, 1.0, 400)
        hw.build()
        ds.brushed_indices = [1, 2, 3]

        assert hw.figure_widget.data[1].selectedpoints == ds.brushed_indices
        assert hw.figure_widget.data[0].visible

    def test_brush_indices_change_deselect(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        ds.brushed_indices = [1, 2, 3]
        hw = HistogramWidget(ds, 0, 0, 1.0, 400)
        hw.build()
        ds.reset_selection()

        assert hw.figure_widget.data[1].selectedpoints == ds.indices
        assert not hw.figure_widget.data[0].visible

    def test_plot_invisible_with_no_data(self, small_df, populated_config):
        ds = DataSource(small_df)
        hw = HistogramWidget(ds, 0, 0, 1.0, 400)
        ds.brushed_indices = []

        assert not hw.figure_widget.data[1].visible

        ds.brushed_indices = [0]
        assert hw.figure_widget.data[1].visible


class TestSelectUI:
    def test_column_select(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        hw = HistogramWidget(ds, 0, 0, 1.0, 400)
        hw.column_select.value = "b"
        assert list(hw.figure_widget.data[0].x) == list(small_df["b"].values)

    def test_normalize_select_true(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        hw = HistogramWidget(ds, 0, 0, 1.0, 400)
        hw.normalize.value = True

        assert hw.figure_widget.data[0].histnorm == "probability"
        assert hw.figure_widget.data[1].histnorm == "probability"

    def test_normalize_select_false(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        hw = HistogramWidget(ds, 0, 0, 1.0, 400)
        hw.normalize.value = False

        assert hw.figure_widget.data[0].histnorm == ""
        assert hw.figure_widget.data[1].histnorm == ""
