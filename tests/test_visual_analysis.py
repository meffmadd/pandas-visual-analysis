import pytest
from traitlets import TraitError

from pandas_visual_analysis import VisualAnalysis
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


def test_visual_analysis_object_creation(small_df):
    assert VisualAnalysis(small_df)


def test_visual_analysis_object_creation_non_int_index(small_df_index):
    assert VisualAnalysis(small_df_index)


def test_visual_analysis_object_creation_color(small_df):
    assert VisualAnalysis(small_df, select_color='#ffffff', deselect_color=(0, 0, 0))


# noinspection PyTypeChecker
def test_visual_analysis_object_creation_color_error(small_df):
    with pytest.raises(TraitError):
        VisualAnalysis(small_df, select_color=(0, 0))


def test_visual_analysis_object_creation_color_error2(small_df):
    with pytest.raises(ValueError):
        VisualAnalysis(small_df, select_color="#asdfasdfa")


def test_visual_analysis_alpha_error(small_df):
    with pytest.raises(TraitError):
        VisualAnalysis(small_df, alpha=1.4)


def test_visual_analysis_color_trait_error(small_df):
    with pytest.raises(TraitError):
        VisualAnalysis(small_df, select_color=(500, 0, 0))


def test_visual_analysis_sample_number(int_df):
    va = VisualAnalysis(int_df, sample=100)
    assert len(va.df) == 100


def test_visual_analysis_sample_frac(int_df):
    va = VisualAnalysis(int_df, sample=0.5)
    assert len(va.df) == 500


def test_visual_analysis_sample_number_neg_error(int_df):
    with pytest.raises(ValueError):
        VisualAnalysis(int_df, sample=-100)


def test_visual_analysis_sample_frac_neg_error(int_df):
    with pytest.raises(ValueError):
        VisualAnalysis(int_df, sample=-0.4)


def test_visual_analysis_sample_number_large_error(int_df):
    with pytest.raises(ValueError):
        VisualAnalysis(int_df, sample=10000)


def test_visual_analysis_sample_frac_large_error(int_df):
    with pytest.raises(ValueError):
        VisualAnalysis(int_df, sample=10.4)


# noinspection PyTypeChecker
def test_visual_analysis_sample_input_error(int_df):
    with pytest.raises(TypeError):
        VisualAnalysis(int_df, sample="asdfa")


def test_visual_analysis_display_system(int_df):
    va = VisualAnalysis(int_df, None, [['Scatter']])
    from IPython.core.display import display
    display((va,))