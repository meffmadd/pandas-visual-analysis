import pytest
import ipywidgets as widgets

from pandas_visual_analysis import DataSource
from pandas_visual_analysis.utils.config import Config
from pandas_visual_analysis.widgets import ParallelCoordinatesWidget
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
    config.color_scale = [[0, 'rgb(%d,%d,%d)' % config.deselect_color], [1, 'rgb(%d,%d,%d)' % config.select_color]]


def fill_sample_constraint_range(dimensions, col, constraint_range):
    for dim in dimensions:
        if dim.label != col:
            continue
        dim['constraintrange'] = constraint_range
    return dimensions


class TestInit:

    def test_object_creation(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        ParallelCoordinatesWidget(ds, 0, 0, 1.0, 400)


class TestBuild:

    def test_normal_build(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        ps = ParallelCoordinatesWidget(ds, 0, 0, 1.0, 400)
        root_widget = ps.build()
        assert isinstance(root_widget, widgets.HBox)

    # todo: test html message when implemented
    def test_normal_few_cols_html(self, small_df, populated_config):
        pass


class TestOnSelectionHelper:

    def test_on_selection_helper_int_range(self, small_df, populated_config):

        def on_selection_assert(trace, points, state):
            assert len(points) == 4
            assert isinstance(points, list)
            assert 0 not in points

        ds = DataSource(small_df, None)
        ps = ParallelCoordinatesWidget(ds, 0, 0, 1.0, 400)
        dimensions = ps.figure_widget.data[0].dimensions
        assert len(dimensions) != 0
        dimensions = fill_sample_constraint_range(dimensions, 'a', [2, 5])
        print(dimensions)

        ps.on_selection = on_selection_assert
        ps._on_selection_helper(None, dimensions)

    def test_on_selection_helper_float_range(self, small_df, populated_config):

        def on_selection_assert(trace, points, state):
            assert len(points) == 4
            assert isinstance(points, list)
            assert 0 not in points

        ds = DataSource(small_df, None)
        ps = ParallelCoordinatesWidget(ds, 0, 0, 1.0, 400)
        dimensions = ps.figure_widget.data[0].dimensions
        assert len(dimensions) != 0
        dimensions = fill_sample_constraint_range(dimensions, 'a', [1.5, 5])
        print(dimensions)

        ps.on_selection = on_selection_assert
        ps._on_selection_helper(None, dimensions)

    def test_on_selection_helper_no_ranges_deselect(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        ps = ParallelCoordinatesWidget(ds, 0, 0, 1.0, 400)
        ds.brushed_indices = [1, 2]

        dimensions = ps.figure_widget.data[0].dimensions  # no constraint ranges
        ps._on_selection_helper(None, dimensions)  # trigger deselect

        assert len(ds.brushed_indices) == ds.len




class TestOnSelection:

    def test_on_selection(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        ps = ParallelCoordinatesWidget(ds, 0, 0, 1.0, 400)

        points = [1, 2, 3]
        ps.on_selection(None, points, None)

        assert sum(list(ps.figure_widget.data[0].line.color)) == 3
        assert ds.brushed_indices == points


class TestBrushIndicesChange:

    def test_brush_indices_change(self,small_df, populated_config):
        ds = DataSource(small_df, None)
        ps = ParallelCoordinatesWidget(ds, 0, 0, 1.0, 400)

        dimensions = ps.figure_widget.data[0].dimensions
        assert len(dimensions) != 0
        dimensions = fill_sample_constraint_range(dimensions, 'a', [1.5, 5])
        ps.figure_widget.data[0].dimensions = dimensions

        ps.change_initiated = False

        ds._brushed_indices = [1, 2, 3]

        assert sum(list(ps.figure_widget.data[0].line.color)) == 3
        dimensions = ps.figure_widget.data[0].dimensions
        for dimension in dimensions:
            if dimension.label == 'a':
                assert dimension['constraintrange'] is None
                break

