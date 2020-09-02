import pytest
import pandas as pd
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


@pytest.fixture(scope="module")
def mpg_df():
    import os

    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, "./mpg.csv")
    df = pd.read_csv(filename)
    yield df


def test_default(mpg_df):
    from pandas_visual_analysis import VisualAnalysis

    df = mpg_df

    VisualAnalysis(df)


def test_with_data_source(mpg_df):
    from pandas_visual_analysis import VisualAnalysis, DataSource

    df = mpg_df

    ds = DataSource(df)
    VisualAnalysis(ds)


def test_with_cat_cols(mpg_df):
    from pandas_visual_analysis import VisualAnalysis

    df = mpg_df

    VisualAnalysis(
        df, categorical_columns=["name", "origin", "model_year", "cylinders"]
    )


def test_widget_list_output_against_documentation():
    from pandas_visual_analysis import VisualAnalysis

    lst = [
        "Scatter",
        "ParallelCoordinates",
        "BrushSummary",
        "Histogram",
        "ParallelCategories",
        "BoxPlot",
    ]

    assert VisualAnalysis.widgets() == lst


# Test for: visual_analysis.rst


def test_visual_analysis_row_height(mpg_df):
    from pandas_visual_analysis import VisualAnalysis

    VisualAnalysis(mpg_df, row_height=300)


def test_visual_analysis_row_height_list(mpg_df):
    from pandas_visual_analysis import VisualAnalysis

    VisualAnalysis(
        mpg_df,
        layout=[["Scatter", "Scatter"], ["ParallelCoordinates"]],
        row_height=[200, 300],
    )


def test_visual_analysis_sample(mpg_df):
    from pandas_visual_analysis import VisualAnalysis

    va = VisualAnalysis(mpg_df, sample=100)

    assert len(va.data_source) == 100


def test_visual_analysis_alpha(mpg_df):
    from pandas_visual_analysis import VisualAnalysis

    VisualAnalysis(mpg_df, select_color="#323EEC", deselect_color="#8A8C93", alpha=0.75)
