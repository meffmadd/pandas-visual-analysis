import pytest
from traitlets import observe, TraitError, HasTraits

from pandas_visual_analysis import DataSource
from tests import sample_dataframes

df_size = 1000


@pytest.fixture(scope="module")
def small_df():
    return sample_dataframes.small_df()


@pytest.fixture(scope="module")
def small_df_index():
    return sample_dataframes.small_df_non_int_index()


@pytest.fixture(scope="module")
def randint_df():
    return sample_dataframes.randint_df(df_size)


class TestInit:
    def test_brush_selection_object_creation(self, small_df):
        DataSource(small_df, None)

    def test_brush_selection_object_creation_with_catcol(self, small_df):
        DataSource(small_df, ["b", "e"])


class TestColumnAssignments:
    def test_with_catcol_time_cols(self, small_df):
        bs = DataSource(small_df, ["b", "e"])
        assert bs.time_columns == ["d"]

    def test_without_catcol(self, small_df):
        bs = DataSource(small_df, None)
        assert bs.categorical_columns == ["b", "e"]
        assert bs.time_columns == ["d"]
        assert bs.numerical_columns == ["a", "c"]

    def test_columns(self, small_df):
        bs = DataSource(small_df, None)
        assert bs.columns == ["a", "b", "c", "d", "e"]

    def test_columns_only_int(self, randint_df):
        bs = DataSource(randint_df, None)
        assert bs.categorical_columns == []
        assert bs.time_columns == []
        assert bs.numerical_columns == list(randint_df.columns.values)

    def test_brush_selection_catcol_not_present(self, small_df):
        with pytest.raises(ValueError):
            DataSource(small_df, ["unknown"])

    # noinspection PyTypeChecker
    def test_wrong_catcol_arg(self, small_df):
        with pytest.raises(TypeError):
            DataSource(small_df, "unknown")

    def test_data_source_date_time_as_category(self, small_df):
        assert "datetime64" in str(small_df["d"].dtype)
        DataSource(small_df, categorical_columns=["b", "d", "e"])

    def test_data_source_string_col_not_in_cat_cols(self, small_df):
        assert "object" in str(small_df["b"].dtype)
        with pytest.raises(ValueError):
            DataSource(small_df, categorical_columns=["a"])


class TestIndicesData:
    def test_brush_selection_indices(self, randint_df):
        bs = DataSource(randint_df, None)
        assert bs.indices == list(range(df_size))

    def test_reset_selection(self, small_df):
        bs = DataSource(small_df, None)
        bs.brushed_indices = [0]
        assert bs.brushed_indices == [0]
        bs.reset_selection()
        assert bs.brushed_indices == list(range(len(small_df)))

    def test__data(self, small_df):
        bs = DataSource(small_df, None)
        assert list(bs.data.columns.values) == list(small_df.columns.values)

    def test_brushed_indices_and_data(self, small_df_index):
        bs = DataSource(small_df_index, None)
        assert len(bs.brushed_indices) == len(bs.brushed_data)

    def test_data_source_bool_col_not_in_cat_cols(self, small_df):
        assert "bool" in str(small_df["e"].dtype)
        with pytest.raises(ValueError):
            DataSource(small_df, categorical_columns=["b"])


class TestObserve:
    def test_brush_selection_observe_brushed_indices(self, small_df_index):
        bs = DataSource(small_df_index, None)

        def simple_observe(change):
            assert change["old"] == list(range(len(small_df_index)))
            assert change["new"] == [0]

        HasTraits.observe(bs, simple_observe, "_brushed_indices")
        bs._brushed_indices = [0]

    def test_brush_selection_observe_brushed_data(self, small_df_index):
        bs = DataSource(small_df_index, None)

        def simple_observe(change):
            assert len(change["old"]) == len(small_df_index)
            assert len(change["new"]) == 1

        HasTraits.observe(bs, handler=simple_observe, names="_brushed_data")
        bs._brushed_indices = [0]


class TestDataParameter:
    # noinspection PyTypeChecker
    def test_brush_selection_wrong_df(self):
        with pytest.raises(TypeError):
            DataSource([1, 2], None)

    def test_data_source_too_few_cols_error(self, small_df):
        with pytest.raises(ValueError):
            DataSource(small_df[["a"]], None)


class TestLen:
    def test_data_source_len_method(self, small_df):
        ds = DataSource(small_df, None)
        assert len(ds) == len(small_df)

    def test_len(self, randint_df):
        bs = DataSource(randint_df, None)
        assert bs.len == df_size


class TestSample:
    def test_sample_int(self, small_df):
        assert DataSource(small_df, None, 3)

    def test_sample_float(self, small_df):
        assert DataSource(small_df, None, 0.5)

    def test_sample_type_error(self, small_df):
        with pytest.raises(TypeError):
            DataSource(small_df, None, "0.4")


class TestSeed:
    def test_seed_normal(self, small_df):
        DataSource(small_df, seed=10)

    def test_seed_lower(self, small_df):
        DataSource(small_df, seed=0)

    def test_seed_upper(self, small_df):
        DataSource(small_df, seed=(2 ** 32 - 1))

    def test_seed_lower_error(self, small_df):
        with pytest.raises(ValueError):
            DataSource(small_df, seed=-1)

    def test_seed_upper_error(self, small_df):
        with pytest.raises(ValueError):
            DataSource(small_df, seed=2 ** 32)

    def test_seed_type_errro(self, small_df):
        with pytest.raises(TypeError):
            DataSource(small_df, seed="ten")
