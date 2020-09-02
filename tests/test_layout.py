import pytest
from unittest.mock import ANY, Mock, call
from ipywidgets import widgets

from pandas_visual_analysis.layout import AnalysisLayout
from pandas_visual_analysis.data_source import DataSource, SelectionType
from pandas_visual_analysis.utils.config import Config
from pandas_visual_analysis.widgets import WidgetClassRegistry
from pandas_visual_analysis.widgets.scatter import ScatterWidget
from tests import sample_dataframes

df_size = 1000


@pytest.fixture(scope="module")
def populated_config():
    config = Config()
    config.alpha = 0.75
    config.select_color = (0, 0, 0)
    config.deselect_color = (0, 0, 0)


@pytest.fixture(scope="module")
def small_df():
    return sample_dataframes.small_df()


@pytest.fixture(scope="module")
def small_df_index():
    return sample_dataframes.small_df_non_int_index()


@pytest.fixture(scope="module")
def randint_df():
    return sample_dataframes.randint_df(df_size)


def test_analysis_layout_one_num_col_no_warning(small_df):
    assert AnalysisLayout([["Scatter"]], 400, DataSource(small_df, None))


class TestBuild:
    def test_analysis_layout_build(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        layout = AnalysisLayout([["Scatter"], ["Scatter"]], 400, ds)
        root_widget = layout.build()
        assert isinstance(root_widget, widgets.VBox)
        children = root_widget.children
        assert (
            len(children) == 4
        )  # 2 + 2 for HTML(css) and selection types (standard, additive, subtractive)
        assert isinstance(children[1], widgets.HBox)
        assert isinstance(children[2], widgets.HBox)
        assert len(children[1].children) == 1
        assert len(children[2].children) == 1

    def test_build_row_height_list(self, small_df, populated_config):
        ds = DataSource(small_df, None)
        build_return = widgets.HBox()

        scatterInstance = Mock()
        scatterInstance.build = Mock(return_value=build_return)

        mockScatterClass = Mock(return_value=scatterInstance)

        wcr = WidgetClassRegistry()
        wcr.registry["Scatter"] = mockScatterClass
        layout = AnalysisLayout([["Scatter"], ["Scatter"]], [300, 200], ds)
        layout.build()
        call1 = call(ANY, ANY, ANY, ANY, 300)
        call2 = call(ANY, ANY, ANY, ANY, 200)
        mockScatterClass.assert_has_calls([call1, call2], any_order=False)


class TestLayoutSpec:
    def test_analysis_layout_wrong_predefined_layout_error(self, small_df):
        with pytest.raises(ValueError):
            AnalysisLayout("some_unknown_layout", 400, DataSource(small_df, None))

    def test_analysis_layout_wrong_layout_type_error(self, small_df):
        with pytest.raises(TypeError):
            AnalysisLayout(set(["A", "B"]), 400, DataSource(small_df, None))

    def test_analysis_layout_incorrect_widget_name(self, small_df):
        with pytest.raises(ValueError):
            AnalysisLayout([["asdfasdf"]], 400, DataSource(small_df, None))


class TestRowHeight:
    def test_int_normal(self, small_df):
        AnalysisLayout("default", 400, DataSource(small_df))

    def test_int_negative(self, small_df):
        with pytest.raises(ValueError):
            AnalysisLayout("default", -200, DataSource(small_df))

    def test_type_error(self, small_df):
        with pytest.raises(TypeError):
            AnalysisLayout("default", "400px", DataSource(small_df))

    def test_type_error_nested(self, small_df):
        with pytest.raises(TypeError):
            AnalysisLayout("default", ["400px"], DataSource(small_df))

    def test_list_normal(self, small_df):
        AnalysisLayout([["Scatter"], ["Scatter"]], [200, 300], DataSource(small_df))

    def test_list_short(self, small_df):
        with pytest.raises(ValueError):
            AnalysisLayout([["Scatter"], ["Scatter"]], [200], DataSource(small_df))

    def test_list_long(self, small_df):
        with pytest.raises(ValueError):
            AnalysisLayout(
                [["Scatter"], ["Scatter"]], [200, 300, 400], DataSource(small_df)
            )

    def test_list_negative(self, small_df):
        with pytest.raises(ValueError):
            AnalysisLayout(
                [["Scatter"], ["Scatter"]], [200, -300], DataSource(small_df)
            )


class TestSelectionType:
    def test_std_standard(self, small_df):
        ds = DataSource(small_df, None)
        layout = AnalysisLayout([["Scatter"], ["Scatter"]], 400, ds)
        assert layout.data_source.selection_type == SelectionType.STANDARD

    def test_change_to_std(self, small_df):
        ds = DataSource(small_df, None)
        layout = AnalysisLayout([["Scatter"], ["Scatter"]], 400, ds)
        layout.selection_type_widget.value = (
            "add"  # change first so observe gets triggered
        )
        layout.selection_type_widget.value = "std"
        assert layout.data_source.selection_type == SelectionType.STANDARD

    def test_change_to_add(self, small_df):
        ds = DataSource(small_df, None)
        layout = AnalysisLayout([["Scatter"], ["Scatter"]], 400, ds)
        layout.selection_type_widget.value = "add"
        assert layout.data_source.selection_type == SelectionType.ADDITIVE

    def test_change_to_sub(self, small_df):
        ds = DataSource(small_df, None)
        layout = AnalysisLayout([["Scatter"], ["Scatter"]], 400, ds)
        layout.selection_type_widget.value = "sub"
        assert layout.data_source.selection_type == SelectionType.SUBTRACTIVE
