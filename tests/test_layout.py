import pytest
from ipywidgets import widgets

from pandas_visual_analysis.layout import AnalysisLayout
from pandas_visual_analysis.data_source import DataSource
from pandas_visual_analysis.utils.config import Config
from tests import sample_dataframes

df_size = 1000


@pytest.fixture
def populated_config():
    config = Config()
    config.alpha = 0.75
    config.select_color = (0, 0, 0)
    config.deselect_color = (0, 0, 0)


@pytest.fixture
def small_df():
    return sample_dataframes.small_df()


@pytest.fixture
def small_df_index():
    return sample_dataframes.small_df_non_int_index()


@pytest.fixture
def randint_df():
    return sample_dataframes.randint_df(df_size)


# todo: update when ParallelCoordinatesWidget exists
# def test_analysis_layout_warns_one_num_col(small_df):
#     with pytest.warns(UserWarning):
#         AnalysisLayout(small_df[['a', 'b', 'd', 'e']], None, [['ParallelCoordinates']], (0, 0, 0), (0, 0, 0), 0.75)


def test_analysis_layout_one_num_col_no_warning(small_df):
    assert AnalysisLayout([['Scatter']], DataSource(small_df, None))


def test_analysis_layout_incorrect_widget_name(small_df):
    with pytest.raises(ValueError):
        AnalysisLayout([['asdfasdf']], DataSource(small_df, None))


def test_analysis_layout_build(small_df, populated_config):
    ds = DataSource(small_df, None)
    layout = AnalysisLayout([['Scatter'], ['Scatter']], ds)
    root_widget = layout.build()
    assert isinstance(root_widget, widgets.VBox)
    children = root_widget.children
    assert len(children) == 2
    assert isinstance(children[0], widgets.HBox)
    assert isinstance(children[1], widgets.HBox)
    assert len(children[0].children) == 1
    assert len(children[1].children) == 1

