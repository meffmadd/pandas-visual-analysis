import pytest

from pandas_visual_analysis import DataSource
from pandas_visual_analysis.widgets import BaseWidget
from tests import sample_dataframes


@pytest.fixture(scope="module")
def small_df():
    return sample_dataframes.small_df()


#  for coverage
def test_base_widget_abstract_methods(small_df):
    BaseWidget.__abstractmethods__ = set()

    class Dummy(BaseWidget):
        pass

    d = Dummy(DataSource(small_df), 0, 0, 1.0, 400)

    d.on_deselection(None, None)
    d.observe_brush_indices_change(None)
    d.build()
    d.on_selection(None, None, None)
    d.set_observers()


def test_validate_data_source(small_df):
    with pytest.raises(TypeError):
        BaseWidget(small_df, 0, 0, 0.3, 100)
