import pytest
import pandas as pd
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


@pytest.fixture(scope="module")
def mpg_df():
    df = pd.read_csv("./mpg.csv")
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
