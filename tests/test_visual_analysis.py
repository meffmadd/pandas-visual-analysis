import pytest

from pandas_visual_analysis import VisualAnalysis, DataSource
from tests import sample_dataframes


@pytest.fixture
def small_df():
    return sample_dataframes.small_df()


@pytest.fixture
def small_df_index():
    return sample_dataframes.small_df_non_int_index()


@pytest.fixture
def int_df():
    return sample_dataframes.randint_df(1000)


class TestInit:
    def test_visual_analysis_object_creation(self, small_df):
        assert VisualAnalysis(small_df)

    def test_visual_analysis_object_creation_non_int_index(self, small_df_index):
        assert VisualAnalysis(small_df_index)

    def test_init_with_data_source(self, small_df):
        ds = DataSource(small_df, None)
        assert VisualAnalysis(data=ds)

    def test_data_type_error(self):
        with pytest.raises(TypeError):
            VisualAnalysis(data=[1, 2, 3])


class TestColor:
    def test_visual_analysis_color_tuple(self, small_df):
        assert VisualAnalysis(small_df, select_color=(12, 12, 12))

    def test_visual_analysis_object_creation_color(self, small_df):
        assert VisualAnalysis(
            small_df, select_color="#ffffff", deselect_color=(0, 0, 0)
        )

    # noinspection PyTypeChecker
    def test_visual_analysis_object_creation_color_error(self, small_df):
        with pytest.raises(ValueError):
            VisualAnalysis(small_df, select_color=(0, 0))

    # noinspection PyTypeChecker
    def test_visual_analysis_object_creation_deselect_color_error(self, small_df):
        with pytest.raises(ValueError):
            VisualAnalysis(small_df, deselect_color=(0, 0))

    # noinspection PyTypeChecker
    def test_visual_analysis_object_creation_color_high_value_error(self, small_df):
        with pytest.raises(ValueError):
            VisualAnalysis(small_df, deselect_color=(0, 0, 500))

    # noinspection PyTypeChecker
    def test_visual_analysis_object_creation_select_color_type_error(self, small_df):
        with pytest.raises(TypeError):
            VisualAnalysis(small_df, select_color=set([0, 0, 0]))

    # noinspection PyTypeChecker
    def test_visual_analysis_object_creation_deselect_color_type_error(self, small_df):
        with pytest.raises(TypeError):
            VisualAnalysis(small_df, deselect_color=set([0, 0, 0]))

    def test_visual_analysis_object_creation_color_error2(self, small_df):
        with pytest.raises(ValueError):
            VisualAnalysis(small_df, select_color="#asdfasdfa")

    def test_visual_analysis_color_value_error(self, small_df):
        with pytest.raises(ValueError):
            VisualAnalysis(small_df, select_color=(500, 0, 0))


class TestAlpha:

    # noinspection PyTypeChecker
    def test_visual_analysis_object_creation_alpha_type_error(self, small_df):
        with pytest.raises(TypeError):
            VisualAnalysis(small_df, alpha=[0.5])

    def test_visual_analysis_alpha_error(self, small_df):
        with pytest.raises(ValueError):
            VisualAnalysis(small_df, alpha=1.4)


class TestSample:
    def test_visual_analysis_sample_number_neg_error(self, int_df):
        with pytest.raises(ValueError):
            VisualAnalysis(int_df, sample=-100)

    def test_visual_analysis_sample_frac_neg_error(self, int_df):
        with pytest.raises(ValueError):
            VisualAnalysis(int_df, sample=-0.4)

    def test_visual_analysis_sample_number_large_error(self, int_df):
        with pytest.raises(ValueError):
            VisualAnalysis(int_df, sample=10000)

    def test_visual_analysis_sample_frac_large_error(self, int_df):
        with pytest.raises(ValueError):
            VisualAnalysis(int_df, sample=10.4)

    # noinspection PyTypeChecker
    def test_visual_analysis_sample_input_error(self, int_df):
        with pytest.raises(TypeError):
            VisualAnalysis(int_df, sample="asdfa")


class TestDisplay:
    def test_visual_analysis_display_system(self, int_df):
        va = VisualAnalysis(int_df, [["Scatter"]])
        from IPython.core.display import display

        display((va,))

    def test_ipython_display(self, small_df):
        va = VisualAnalysis(small_df)
        va._ipython_display_()


class TestPlotTypeWarn:
    def test_visual_analysis_warn_num_cols(self, small_df):
        small_df.drop(columns=["c"], inplace=True)
        with pytest.warns(UserWarning):
            VisualAnalysis(small_df, layout=[["ParallelCoordinates"]])

    def test_warn_cat_cols(self, small_df):
        small_df.drop(columns=["b"], inplace=True)
        with pytest.warns(UserWarning):
            VisualAnalysis(small_df, layout=[["ParallelCategories"]])


class TestRowHeight:
    def test_visual_analysis_row_height_type_error(self, small_df):
        with pytest.raises(TypeError):
            VisualAnalysis(small_df, row_height="100px")

    def test_visual_analysis_row_height_neg_error(self, small_df):
        with pytest.raises(ValueError):
            VisualAnalysis(small_df, row_height=-10)


class TestWidgetList:
    def test_get_all_widgets(self, small_df):
        assert isinstance(VisualAnalysis.widgets(), list)
        assert len(VisualAnalysis.widgets()) != 0
