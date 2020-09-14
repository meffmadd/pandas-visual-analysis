import pytest

from pandas_visual_analysis.utils.column_store import ColumnIterator, ColumnStore
from tests import sample_dataframes


@pytest.fixture(scope="module")
def small_df():
    return sample_dataframes.small_df()


class TestColumnIterator:
    def test_len(self):
        column_iterator = ColumnIterator(["1", "2"])
        assert len(column_iterator) == 2

    def test_next(self):
        column_iterator = ColumnIterator(["1", "2"])
        assert next(column_iterator) == "1"
        assert next(column_iterator) == "2"
        assert next(column_iterator) == "1"

    def test_iter(self):
        column_iterator = iter(ColumnIterator(["1", "2"]))
        assert next(column_iterator) == "1"
        assert next(column_iterator) == "2"
        assert next(column_iterator) == "1"


class TestColumnStore:
    def test_next_numerical(self, small_df):
        col_store = ColumnStore(small_df, small_df.columns.values, None)
        assert col_store.next_numerical() == "a"
        assert col_store.next_numerical() == "c"
        assert col_store.next_numerical() == "a"

    def test_next_categorical(self, small_df):
        col_store = ColumnStore(small_df, small_df.columns.values, None)
        assert col_store.next_categorical() == "b"
        assert col_store.next_categorical() == "e"
        assert col_store.next_categorical() == "b"

    def test_next_time(self, small_df):
        col_store = ColumnStore(small_df, small_df.columns.values, None)
        assert col_store.next_time() == "d"
        assert col_store.next_time() == "d"

    def test_next_prefer_numerical(self, small_df):
        col_store = ColumnStore(small_df, small_df.columns.values, None)
        col_list = [col_store.next_prefer_numerical() for _ in range(len(small_df))]
        assert set(col_list) == set(small_df.columns.values)
        assert col_store.next_prefer_numerical() == "a"
        assert col_list[0] == "a"
        #  test second pass
        col_list = [col_store.next_prefer_numerical() for _ in range(len(small_df))]
        assert set(col_list) == set(small_df.columns.values)

    def test_next_prefer_time(self, small_df):
        col_store = ColumnStore(small_df, small_df.columns.values, None)
        col_list = [col_store.next_prefer_time() for _ in range(len(small_df))]
        assert set(col_list) == set(small_df.columns.values)
        assert col_store.next_prefer_time() == "d"
        assert col_list[0] == "d"
        #  test second pass
        col_list = [col_store.next_prefer_time() for _ in range(len(small_df))]
        assert set(col_list) == set(small_df.columns.values)

    def test_next_prefer_categorical(self, small_df):
        col_store = ColumnStore(small_df, small_df.columns.values, None)
        col_list = [col_store.next_prefer_categorical() for _ in range(len(small_df))]
        assert set(col_list) == set(small_df.columns.values)
        assert col_store.next_prefer_categorical() == "b"
        assert col_list[0] == "b"
        #  test second pass
        col_list = [col_store.next_prefer_categorical() for _ in range(len(small_df))]
        assert set(col_list) == set(small_df.columns.values)
