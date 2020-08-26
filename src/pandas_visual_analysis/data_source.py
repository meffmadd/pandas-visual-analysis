import typing

from pandas import DataFrame
from traitlets import HasTraits, Instance, List, observe

import pandas_visual_analysis.utils.validation as validate


class DataSource(HasTraits):
    """

    :param df: the the pandas.DataFrame object
    :param categorical_columns: if given, specifies which columns are to be interpreted as categorical
    """

    _df = Instance(klass=DataFrame)
    _brushed_indices = List()

    def __init__(
        self,
        df: DataFrame,
        categorical_columns: typing.Union[typing.List[str], None],
        sample: typing.Union[float, int, None] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        validate.validate_data_frame(df)
        validate.validate_sample(sample)

        if sample is None:
            self._df = df
        else:
            if isinstance(sample, float):
                if sample < 0.0 or sample > 1.0:
                    raise ValueError(
                        "Sample has to be between 0.0 and 1.0. Invalid value : %d"
                        % sample
                    )
                self._df = df.sample(frac=sample)
            else:
                if sample < 0 or sample > len(df):
                    raise ValueError(
                        "Sample has to be between 0 and the length of the DataFrame (%d). Invalid value: "
                        "%d" % (len(df), sample)
                    )
                self._df = df.sample(n=sample)
        self.columns = list(self._df.columns.values)

        if isinstance(categorical_columns, list):
            if not set(categorical_columns).issubset(set(self.columns)):
                raise ValueError(
                    "All categorical columns have to be present in the DataFrame. Invalid columns: "
                    + str(list(set(categorical_columns).difference(set(self.columns))))
                )
            self.categorical_columns = categorical_columns
            diff = set(
                self._df.select_dtypes(
                    exclude=["number", "datetime", "timedelta", "datetimetz"]
                ).columns.values
            ).difference(set(self.categorical_columns))
            if len(diff) != 0:
                raise ValueError(
                    "Categorical columns have to include all columns with dtype object, bool or category. "
                    + "The following columns were not included in those: %s"
                    % str(list(diff))
                )
            time_cols = list(
                self._df.select_dtypes(
                    include=["datetime", "timedelta", "datetimetz"]
                ).columns.values
            )
            self.time_columns = list(
                set(time_cols).difference(set(self.categorical_columns))
            )
            self.numerical_columns = list(
                set(self.columns).difference(
                    set(self.categorical_columns).union(set(self.time_columns))
                )
            )
            self._df[self.categorical_columns].select_dtypes(
                exclude=["category", object]
            ).astype(dtype="category")
        elif categorical_columns is None:
            self.categorical_columns = list(
                self._df.select_dtypes(
                    exclude=["number", "datetime", "timedelta", "datetimetz"]
                ).columns.values
            )
            self.time_columns = list(
                self._df.select_dtypes(
                    include=["datetime", "timedelta", "datetimetz"]
                ).columns.values
            )
            self.numerical_columns = list(
                self._df.select_dtypes(include=["number"]).columns.values
            )
        else:
            raise TypeError(
                "Categorical columns have to be specified with a list of strings or have to be omitted "
                "with None."
            )

        self._length = len(df)
        self._indices = list(range(self._length))
        self.reset_selection()

        self.brushed_data_invalidated = True
        self._brushed_data = None

        if len(self.columns) < 2:
            raise ValueError(
                "The passed DataFrame only has %d column, which is insufficient for analysis."
                % len(self.columns)
            )

        self.few_num_cols = len(self.numerical_columns) < 2
        self.few_cat_cols = len(self.categorical_columns) < 2

    def reset_selection(self):
        self._brushed_indices = self._indices

    @property
    def len(self) -> int:
        """
        :return: Returns the length of the DataFrame
        """
        return self._length

    def __len__(self):
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
    def brushed_data(self) -> DataFrame:
        """
        Only determines brushed data if it was invalidated by new selected indices.
        This gives more efficiency if only the brushed indices are needed and not the brushed data.
        :return: Returns the selected data corresponding to the indices.
        """
        if self.brushed_data_invalidated:
            self._brushed_data = self._df.iloc[self._brushed_indices, :]
            self.brushed_data_invalidated = False
        return self._brushed_data

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

    @observe("_brushed_indices")
    def _observe_indices(self, change):
        self.brushed_data_invalidated = True
