import pytest
import ipywidgets as widgets

from pandas_visual_analysis import DataSource
from pandas_visual_analysis.utils.config import Config
from pandas_visual_analysis.widgets import ParallelCategoriesWidget
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
        ParallelCategoriesWidget(ds, 0, 0, 1.0, 400)

    def test_normal_few_cols_html(self, small_df, populated_config):
        df = small_df.drop(columns=["b", "e"])
        ds = DataSource(df, None)
        with pytest.raises(ValueError):
            ParallelCategoriesWidget(ds, 0, 0, 1.0, 400)


class TestBuild:
    def test_normal_build(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        pc = ParallelCategoriesWidget(ds, 0, 0, 1.0, 400)
        root_widget = pc.build()
        assert isinstance(root_widget, widgets.HBox)


class TestOnSelection:
    def test_on_selection(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        pc = ParallelCategoriesWidget(ds, 0, 0, 1.0, 400)

        points = PointsObject([1, 2, 3])
        pc.on_selection(None, points, None)

        assert sum(list(pc.figure_widget.data[0].line.color)) == 3
        assert ds.brushed_indices == set(points.point_inds)

    def test_on_deselection(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        pc = ParallelCategoriesWidget(ds, 0, 0, 1.0, 400)
        pc.on_deselection(None, None)


class TestBrushIndicesChange:
    def test_brush_indices_change(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        pc = ParallelCategoriesWidget(ds, 0, 0, 1.0, 400)
        ds.brushed_indices = [1, 2, 3]

        assert sum(list(pc.figure_widget.data[0].line.color)) == 3


class TestMultiSelect:
    def test_basic_multi_select(self, rand_cat_df, populated_config):
        ds = DataSource(rand_cat_df, None)
        ParallelCategoriesWidget(ds, 0, 0, 0.2, 400)

    def test_multi_select(self, rand_cat_df, populated_config):
        ds = DataSource(rand_cat_df, None)
        ps = ParallelCategoriesWidget(ds, 0, 0, 0.2, 400)
        ps.multi_select.selected_options = ["A", "B"]
