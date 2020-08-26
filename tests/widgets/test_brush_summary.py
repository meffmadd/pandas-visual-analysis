import math

import pytest
import ipywidgets

from pandas_visual_analysis import DataSource
from pandas_visual_analysis.utils.config import Config
from pandas_visual_analysis.widgets import BrushSummaryWidget
from tests import sample_dataframes


@pytest.fixture(scope="module")
def small_df():
    return sample_dataframes.small_df()


@pytest.fixture(scope="module")
def rand_float_df():
    return sample_dataframes.random_float_df(1000, 10)


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


class TestInit:
    def test_basic_creation(self, small_df):
        ds = DataSource(small_df, None)
        BrushSummaryWidget(ds, 0, 0, 1.0, 300)

    def test_normal_few_cols_error(self, small_df):
        df = small_df.drop(columns=["a", "c"])
        ds = DataSource(df, None)
        with pytest.raises(ValueError):
            BrushSummaryWidget(ds, 0, 0, 1.0, 400)


class TestBuild:
    def test_basic_build(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        bs = BrushSummaryWidget(ds, 0, 0, 1.0, 400)
        root = bs.build()

        assert isinstance(root, ipywidgets.Widget)
        assert isinstance(root, ipywidgets.VBox)
        assert len(root.children) == 2


class TestChanges:
    def test_indices_changed(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        bs = BrushSummaryWidget(ds, 0, 0, 1.0, 400)

        ds.brushed_indices = [0]
        brushed_row = ds.brushed_data
        assert bs.brushed_metrics.loc["mean"]["a"] == brushed_row["a"][0]
        assert bs.brushed_metrics.loc["mean"]["c"] == brushed_row["c"][0]
        assert bs.brushed_metrics["a"]["count"] == 1.0
        assert bs.brushed_metrics["c"]["count"] == 1.0

    def test_metric_changed_basic(self, small_df):
        ds = DataSource(small_df, None)
        bs = BrushSummaryWidget(ds, 0, 0, 1.0, 400)

        bs.metric_select.value = "min"


class TestMapValues:
    def test_basic_map(self):
        assert BrushSummaryWidget._map_value(5, 0, 10, 0, 1) == 0.5

    def test_map_nan(self):
        assert BrushSummaryWidget._map_value(1, math.nan, 2, 0, 1) == 0

    def test_map_bigger(self):
        assert BrushSummaryWidget._map_value(3, 0, 1, 0, 10) == 10

    def test_map_smaller(self):
        assert BrushSummaryWidget._map_value(-1, 0, 10, 0, 1) == 0


class TestSelection:
    def test_selection(self, small_df):
        ds = DataSource(small_df, None)
        bs = BrushSummaryWidget(ds, 0, 0, 1.0, 400)
        bs.on_selection(None, None, None)

    def test_deselection(self, small_df):
        ds = DataSource(small_df, None)
        bs = BrushSummaryWidget(ds, 0, 0, 1.0, 400)
        bs.on_deselection(None, None)
