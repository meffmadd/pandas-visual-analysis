import pytest

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
