from copy import deepcopy

import pytest
import ipywidgets as widgets

from pandas_visual_analysis import DataSource
from pandas_visual_analysis.data_source import SelectionType
from pandas_visual_analysis.utils.config import Config
from pandas_visual_analysis.widgets import ParallelCoordinatesWidget
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


class PointsObject:
    def __init__(self, indices):
        self.point_inds = indices


def fill_sample_constraint_range(dimensions, col, constraint_range):
    for dim in dimensions:
        if dim.label != col:
            continue
        dim["constraintrange"] = constraint_range
    return dimensions


class TestInit:
    def test_object_creation(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        ParallelCoordinatesWidget(ds, 0, 0, 1.0, 400)

    def test_normal_few_cols_html(self, small_df, populated_config):
        df = small_df.drop(columns=["a", "c"])
        ds = DataSource(df, None)
        with pytest.raises(ValueError):
            ParallelCoordinatesWidget(ds, 0, 0, 1.0, 400)


class TestBuild:
    def test_normal_build(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        ps = ParallelCoordinatesWidget(ds, 0, 0, 1.0, 400)
        root_widget = ps.build()
        assert isinstance(root_widget, widgets.HBox)


class TestOnSelectionHelper:
    def test_on_selection_helper_int_range(self, small_df, populated_config):
        def on_selection_assert(trace, points, state):
            assert len(points.point_inds) == 4
            assert isinstance(points.point_inds, list)
            assert 0 not in points.point_inds

        ds = DataSource(small_df, None)
        ps = ParallelCoordinatesWidget(ds, 0, 0, 1.0, 400)
        old_dimensions = deepcopy(
            ps.figure_widget.data[0].dimensions
        )  # no constraint ranges
        assert len(old_dimensions) != 0
        dimensions = fill_sample_constraint_range(old_dimensions, "a", [2, 5])
        print(dimensions)

        ps.on_selection = on_selection_assert
        ps._on_selection_helper(None, dimensions)

    def test_on_selection_helper_float_range(self, small_df, populated_config):
        def on_selection_assert(trace, points, state):
            assert len(points.point_inds) == 4
            assert isinstance(points.point_inds, list)
            assert 0 not in points.point_inds

        ds = DataSource(small_df, None)
        ps = ParallelCoordinatesWidget(ds, 0, 0, 1.0, 400)
        old_dimensions = deepcopy(
            ps.figure_widget.data[0].dimensions
        )  # no constraint ranges
        assert len(old_dimensions) != 0
        dimensions = fill_sample_constraint_range(old_dimensions, "a", [1.5, 5])
        print(dimensions)

        ps.on_selection = on_selection_assert
        ps._on_selection_helper(None, dimensions)

    def test_on_selection_helper_no_ranges_deselect(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        ps = ParallelCoordinatesWidget(ds, 0, 0, 1.0, 400)
        ds.brushed_indices = [1, 2]

        old_dimensions = deepcopy(
            ps.figure_widget.data[0].dimensions
        )  # no constraint ranges
        dimensions = ps.figure_widget.data[0].dimensions
        dimensions = fill_sample_constraint_range(dimensions, "a", [2, 5])
        ps._on_selection_helper(None, dimensions)
        assert len(ds) != 0
        ps._on_selection_helper(None, old_dimensions)  # trigger deselect

        assert len(ds.brushed_indices) == ds.len


class TestOnSelection:
    def test_on_selection(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        ps = ParallelCoordinatesWidget(ds, 0, 0, 1.0, 400)

        points = PointsObject([1, 2, 3])
        ps.on_selection(None, points, None)

        assert sum(list(ps.figure_widget.data[0].line.color)) == 3
        assert ds.brushed_indices == set(points.point_inds)

    def test_on_selection_constraint_ranges_reset(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        ps = ParallelCoordinatesWidget(ds, 0, 0, 1.0, 400)

        dimensions = ps.figure_widget.data[0].dimensions
        assert len(dimensions) != 0
        dimensions = fill_sample_constraint_range(dimensions, "a", [2, 5])
        ps._on_selection_helper(None, dimensions)

        ds.brushed_indices = [1, 2]
        assert ps.constraint_ranges == {}

    @pytest.mark.parametrize(
        "type", [SelectionType.ADDITIVE, SelectionType.SUBTRACTIVE]
    )
    def test_constraint_range_reset_data_source(self, small_df, populated_config, type):
        ds = DataSource(small_df)
        ps = ParallelCoordinatesWidget(ds, 0, 0, 1.0, 400)
        ds.selection_type = type

        dimensions = ps.figure_widget.data[0].dimensions
        assert len(dimensions) != 0
        dimensions = fill_sample_constraint_range(dimensions, "a", [2, 5])
        ps._on_selection_helper(None, dimensions)

        assert ps.constraint_ranges == {}


class TestBrushIndicesChange:
    def test_brush_indices_change(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        ps = ParallelCoordinatesWidget(ds, 0, 0, 1.0, 400)

        dimensions = ps.figure_widget.data[0].dimensions
        assert len(dimensions) != 0
        dimensions = fill_sample_constraint_range(dimensions, "a", [1.5, 5])
        ps.figure_widget.data[0].dimensions = dimensions

        ps.change_initiated = False

        ds.brushed_indices = [1, 2, 3]

        assert sum(list(ps.figure_widget.data[0].line.color)) == 3
        dimensions = ps.figure_widget.data[0].dimensions
        for dimension in dimensions:
            if dimension.label == "a":
                assert dimension["constraintrange"] is None
                break


class TestRedraw:
    def test_redraw_plot_keep_old_constraint_ranges(
        self, rand_float_df, populated_config
    ):
        ds = DataSource(rand_float_df, None)
        ps = ParallelCoordinatesWidget(ds, 0, 0, 0.2, 400)

        dimensions = ps.figure_widget.data[0].dimensions
        assert len(dimensions) != 0
        dimensions = fill_sample_constraint_range(dimensions, "A", [1.5, 5])
        ps.figure_widget.data[0].dimensions = dimensions

        ps.selected_columns = ["A", "B"]
        ps._redraw_plot()

        updated_ranges = {
            dim["label"]: dim["constraintrange"]
            for dim in ps.figure_widget.data[0].dimensions
            if dim["constraintrange"]
        }

        assert list(updated_ranges["A"]) == [1.5, 5]


class TestMultiSelect:
    def test_basic_multi_select(self, rand_float_df, populated_config):
        ds = DataSource(rand_float_df, None)
        ps = ParallelCoordinatesWidget(ds, 0, 0, 0.2, 400)
        assert ps.multi_select is not None

    def test_multi_select(self, rand_float_df, populated_config):
        ds = DataSource(rand_float_df, None)
        ps = ParallelCoordinatesWidget(ds, 0, 0, 0.2, 400)
        ps.multi_select.selected_options = ["A", "B"]
