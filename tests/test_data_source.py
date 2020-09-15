import pytest
import pandas as pd

from pandas_visual_analysis import DataSource
from pandas_visual_analysis.data_source import SelectionType
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


@pytest.fixture(scope="module")
def sample_csv_filepath(tmpdir_factory):
    path = str(tmpdir_factory.mktemp("read_files").join("temp.csv"))
    df = sample_dataframes.small_df()
    df.to_csv(path)
    yield path


@pytest.fixture(scope="module")
def sample_tsv_filepath(tmpdir_factory):
    path = str(tmpdir_factory.mktemp("read_files").join("temp.tsv"))
    df = sample_dataframes.small_df()
    df.to_csv(path, sep="\t")
    yield path


@pytest.fixture(
    scope="module", params=["split", "records", "index", "columns", "values"]
)
def sample_json_filepath(tmpdir_factory, request):
    path = str(tmpdir_factory.mktemp("read_files").join("temp.json"))
    orientation = request.param
    df = sample_dataframes.small_df()
    df.to_json(path, orient=orientation)
    yield path, orientation


@pytest.fixture(scope="module")
def sample_xlsx_filepath(tmpdir_factory):
    path = str(tmpdir_factory.mktemp("read_files").join("temp.xlsx"))
    df = sample_dataframes.small_df()
    df.to_excel(path)
    yield path


@pytest.fixture(scope="module")
def sample_xls_filepath(tmpdir_factory):
    path = str(tmpdir_factory.mktemp("read_files").join("temp.xls"))
    df = sample_dataframes.small_df()
    df.to_excel(path)
    yield path


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
        assert bs.indices == set(range(df_size))

    def test_reset_selection(self, small_df):
        bs = DataSource(small_df, None)
        bs.brushed_indices = [0]
        assert bs.brushed_indices == {0}
        bs.reset_selection()
        assert bs.brushed_indices == set(range(len(small_df)))

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
        ds = DataSource(small_df_index, None)

        def simple_observe(sender: DataSource):
            assert sender.brushed_indices == {0}

        ds.on_indices_changed.connect(simple_observe)
        ds._brushed_indices = [0]

    def test_brush_selection_observe_brushed_data(self, small_df_index):
        ds = DataSource(small_df_index, None)

        def simple_observe(sender: DataSource):
            assert len(sender.brushed_data) == 1

        ds.on_indices_changed.connect(simple_observe)
        ds._brushed_indices = [0]


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
        ds = DataSource(small_df, None, 3)
        assert len(ds) == 3

    def test_sample_float(self, small_df):
        ds = DataSource(small_df, None, 0.5)
        assert len(ds) == len(small_df) // 2

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


class TestSelectionType:
    def test_standard_is_default(self, small_df):
        ds = DataSource(small_df)
        assert ds.selection_type == SelectionType.STANDARD

    def test_standard(self, small_df):
        ds = DataSource(small_df)
        ds.brushed_indices = [1, 2]
        assert ds.brushed_indices == {1, 2}

    def test_additive(self, small_df):
        ds = DataSource(small_df)
        ds.brushed_indices = [1, 2]
        ds.selection_type = SelectionType.ADDITIVE
        ds.brushed_indices = [2, 3]
        assert ds.brushed_indices == {1, 2, 3}

    def test_subtractive(self, small_df):
        ds = DataSource(small_df)
        ds.brushed_indices = [1, 2]
        ds.selection_type = SelectionType.SUBTRACTIVE
        ds.brushed_indices = [2, 3]
        assert ds.brushed_indices == {1}


class TestReadMethods:
    @pytest.mark.parametrize("header", [None, 0])
    def test_read_csv(self, sample_csv_filepath, small_df, header):
        ds = DataSource.read_csv(path=sample_csv_filepath, header=header)
        assert isinstance(ds.data, pd.DataFrame)
        assert (
            len(ds.data) - 1 == len(small_df)
            if header is None
            else len(ds.data) == len(small_df)
        )

    @pytest.mark.parametrize("header", [None, 0])
    def test_read_tsv(self, sample_tsv_filepath, small_df, header):
        ds = DataSource.read_tsv(sample_tsv_filepath, header=header)
        assert isinstance(ds.data, pd.DataFrame)
        assert (
            len(ds.data) - 1 == len(small_df)
            if header is None
            else len(ds.data) == len(small_df)
        )

    def test_read_json(self, sample_json_filepath, small_df):
        path, orientation = sample_json_filepath
        ds = DataSource.read_json(path, orient=orientation)
        assert isinstance(ds.data, pd.DataFrame)
        assert len(ds.data) == len(small_df)

    @pytest.mark.parametrize("extension", ["xlsx", "xls", "html", "txt"])
    def test_read_unsupported(self, extension):
        with pytest.raises(ValueError):
            DataSource.read("./path/to/file.%s" % extension)

    @pytest.mark.parametrize("header", [None, 0])
    def test_read_infer_csv(self, sample_csv_filepath, small_df, header):
        ds = DataSource.read(sample_csv_filepath, header=header)
        assert isinstance(ds.data, pd.DataFrame)
        assert (
            len(ds.data) - 1 == len(small_df)
            if header is None
            else len(ds.data) == len(small_df)
        )

    @pytest.mark.parametrize("header", [None, 0])
    def test_read_infer_tsv(self, sample_tsv_filepath, small_df, header):
        ds = DataSource.read(sample_tsv_filepath, header=header)
        assert isinstance(ds.data, pd.DataFrame)
        assert (
            len(ds.data) - 1 == len(small_df)
            if header is None
            else len(ds.data) == len(small_df)
        )

    def test_read_infer_json(self, sample_json_filepath, small_df):
        path, orientation = sample_json_filepath
        ds = DataSource.read(path, orient=orientation)
        assert isinstance(ds.data, pd.DataFrame)
        assert len(ds.data) == len(small_df)


class TestContextManager:
    @pytest.mark.parametrize("header", [None, 0])
    def test_read_context_csv(self, sample_csv_filepath, small_df, header):
        with DataSource.read(sample_csv_filepath, header) as ds:
            assert isinstance(ds.data, pd.DataFrame)
            assert (
                len(ds.data) - 1 == len(small_df)
                if header is None
                else len(ds.data) == len(small_df)
            )

    @pytest.mark.parametrize("header", [None, 0])
    def test_read_context_tsv(self, sample_tsv_filepath, small_df, header):
        with DataSource.read(sample_tsv_filepath, header) as ds:
            assert isinstance(ds.data, pd.DataFrame)
            assert (
                len(ds.data) - 1 == len(small_df)
                if header is None
                else len(ds.data) == len(small_df)
            )

    def test_read_context_json(self, sample_json_filepath, small_df):
        path, orientation = sample_json_filepath
        with DataSource.read(path, orientation) as ds:
            assert isinstance(ds.data, pd.DataFrame)
            assert len(ds.data) == len(small_df)

    def test_read_context_error(self):
        with pytest.raises(FileNotFoundError):
            with DataSource.read("./some/file.csv") as ds:
                pass
