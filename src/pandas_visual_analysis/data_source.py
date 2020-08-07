import typing

from pandas import DataFrame
from traitlets import HasTraits, Instance, Int, List, observe

from pandas_visual_analysis.utils.util import compare_lists


class DataSource(HasTraits):
    """

    :param df: the the pandas.DataFrame object
    :param categorical_columns: if given, specifies which columns are to be interpreted as categorical
    """
    _df = Instance(klass=DataFrame)
    _length = Int()
    _brushed_indices = List()
    _brushed_data = Instance(klass=DataFrame)
    _indices = None

    def __init__(self, df: DataFrame, categorical_columns: typing.Union[typing.List[str], None], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._df = df
        self.columns = list(self._df.columns.values)

        if isinstance(categorical_columns, list):
            if not set(categorical_columns).issubset(set(self.columns)):
                raise ValueError("All categorical columns have to be present in the DataFrame. Invalid columns: "
                                 + str(list(set(categorical_columns).difference(set(self.columns)))))
            self.categorical_columns = categorical_columns
            time_cols = list(self._df.select_dtypes(include=['datetime', 'timedelta', 'datetimetz']).columns.values)
            self.time_columns = list(set(time_cols).difference(set(self.categorical_columns)))
            self.numerical_columns = list(set(self.columns).difference(set(self.categorical_columns).union(set(self.time_columns))))
            self._df[self.categorical_columns].select_dtypes(exclude=['category', object]).astype(dtype='category')
        elif categorical_columns is None:
            self.categorical_columns = list(self._df.select_dtypes(exclude=['number', 'datetime', 'timedelta', 'datetimetz']).columns.values)
            self.time_columns = list(self._df.select_dtypes(include=['datetime', 'timedelta', 'datetimetz']).columns.values)
            self.numerical_columns = list(self._df.select_dtypes(include=['number']).columns.values)
        else:
            raise TypeError("Categorical columns have to be specified with a list of strings or have to be omitted "
                            "with None.")

        self._length = len(df)
        self._indices = list(range(self._length))
        self.reset_selection()

        if len(self.columns) < 2:
            raise ValueError("The passed DataFrame only has %d column, which is insufficient for analysis." %
                             len(self.columns))

        self.few_num_cols = len(self.numerical_columns) < 2

    def reset_selection(self):
        self._brushed_indices = self._indices

    @property
    def len(self) -> int:
        """
        :return: Returns the length of the DataFrame
        """
        return self._length

    @property
    def brushed_indices(self) -> typing.List[int]:
        """
        :return: Returns the selected indices.
        """
        return self._brushed_indices

    @brushed_indices.setter
    def brushed_indices(self, indices: typing.List[int]):
        """
        Selects specified indices in the DataFrame
        :param indices: indices of data points that are brushed
        """
        self._brushed_indices = indices

    @property
    def indices(self) -> typing.List[int]:
        """
        :return: Returns all indices of the data frame. This is a list from 0 to len-1.
        """
        return self._indices

    @property
    def data(self) -> DataFrame:
        """
        :return: The DataFrame for this :class:`pandas_visual_analysis.data_source.DataSource` object.
        """
        return self._df

    @observe('_brushed_indices')
    def _observe_indices(self, change):
        indices = change['new']
        self._brushed_data = self._df.iloc[indices, :]
