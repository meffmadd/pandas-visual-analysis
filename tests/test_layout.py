import pytest
from traitlets import observe, TraitError

from pandas_visual_analysis.layout import AnalysisLayout
from pandas_visual_analysis.data_source import DataSource
from tests import sample_dataframes

df_size = 1000


@pytest.fixture
def small_df():
    return sample_dataframes.small_df()


@pytest.fixture
def small_df_index():
    return sample_dataframes.small_df_non_int_index()


@pytest.fixture
def randint_df():
    return sample_dataframes.randint_df(df_size)


def test_brush_selection_object_creation(small_df):
    DataSource(small_df, None)


def test_brush_selection_object_creation_with_catcol(small_df):
    DataSource(small_df, ['b', 'e'])


def test_brush_selection_with_catcol_time_cols(small_df):
    bs = DataSource(small_df, ['b', 'e'])
    assert bs.time_columns == ['d']


def test_brush_selection_without_catcol(small_df):
    bs = DataSource(small_df, None)
    assert bs.categorical_columns == ['b', 'e']
    assert bs.time_columns == ['d']
    assert bs.numerical_columns == ['a', 'c']


def test_brush_selection_columns(small_df):
    bs = DataSource(small_df, None)
    assert bs.columns == ['a', 'b', 'c', 'd', 'e']


def test_brush_selection_columns_only_int(randint_df):
    bs = DataSource(randint_df, None)
    assert bs.categorical_columns == []
    assert bs.time_columns == []
    assert bs.numerical_columns == list(randint_df.columns.values)


def test_brush_selection_len(randint_df):
    bs = DataSource(randint_df, None)
    assert bs.len == df_size


def test_brush_selection_indices(randint_df):
    bs = DataSource(randint_df, None)
    assert bs.indices == list(range(df_size))


def test_brush_selection_catcol_not_present(small_df):
    with pytest.raises(ValueError):
        DataSource(small_df, ['unknown'])


# noinspection PyTypeChecker
def test_brush_selection_wrong_catcol_arg(small_df):
    with pytest.raises(TypeError):
        DataSource(small_df, 'unknown')


def test_brush_selection_reset_selection(small_df):
    bs = DataSource(small_df, None)
    bs.brushed_indices = [0]
    assert bs.brushed_indices == [0]
    bs.reset_selection()
    assert bs.brushed_indices == list(range(len(small_df)))


def test_brush_selection_data(small_df):
    bs = DataSource(small_df, None)
    assert list(bs.data.columns.values) == list(small_df.columns.values)


def test_brush_selection_brushed_indices_and_data(small_df_index):
    bs = DataSource(small_df_index, None)
    assert len(bs._brushed_indices) == len(bs._brushed_data)


def test_brush_selection_observe_brushed_indices(small_df_index):
    bs = DataSource(small_df_index, None)

    @observe('bs._brushed_indices')
    def simple_observe(change):
        assert change['old'] == list(range(len(small_df_index)))
        assert change['new'] == [0]

    bs._brushed_indices = [0]


def test_brush_selection_observe_brushed_data(small_df_index):
    bs = DataSource(small_df_index, None)

    @observe('bs._brushed_data')
    def simple_observe(change):
        assert len(change['old']) == len(small_df_index)
        assert len(change['new']) == 1

    bs._brushed_indices = [0]


# noinspection PyTypeChecker
def test_brush_selection_wrong_df():
    with pytest.raises(TraitError):
        DataSource([1, 2], None)


def test_analysis_layout_one_column_df(small_df):
    with pytest.raises(ValueError):
        AnalysisLayout([['ParallelCoordinates']], DataSource(small_df, None))

# todo: update when ParallelCoordinatesWidget exists
# def test_analysis_layout_warns_one_num_col(small_df):
#     with pytest.warns(UserWarning):
#         AnalysisLayout(small_df[['a', 'b', 'd', 'e']], None, [['ParallelCoordinates']], (0, 0, 0), (0, 0, 0), 0.75)


def test_analysis_layout_one_num_col_no_warning(small_df):
    assert AnalysisLayout([['Scatter']], DataSource(small_df, None))


def test_analysis_layout_incorrect_widget_name(small_df):
    with pytest.raises(ValueError):
        AnalysisLayout([['asdfasdf']], DataSource(small_df, None))

# todo: test AnalysisLayout once it is fully implemented
