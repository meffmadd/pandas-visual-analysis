import typing
from enum import Enum
from blinker import Signal
from pandas import DataFrame

import pandas_visual_analysis.utils.validation as validate


class SelectionType(Enum):
    STANDARD = 1
    ADDITIVE = 2
    SUBTRACTIVE = 3


class DataSource:

    """
    The DataSource object provides the data itself to the plots and also manages the brushing between the plots.
    If the plots observe the brushed_indices property of this class, they can react to any change in the data.
    It is also possible to set the brushed_indices property to trigger the change in any instances that observe
    this property. In addition to the brushed indices, this class also provides the brushed data directly, which
    is cached to speed up subsequent access to the data.
    """

    def __init__(
        self,
        df: DataFrame,
        categorical_columns: typing.Union[typing.List[str], None] = None,
        sample: typing.Union[float, int, None] = None,
        seed: typing.Union[int, None] = None,
        *args,
        **kwargs
    ):
        """

        :param df: A pandas.DataFrame object.
        :param categorical_columns: If given, specifies which columns are to be interpreted as categorical.
            Those columns have to include all columns of the DataFrame
            which have type `object`, `str`, `bool` or `category`.
            This means it can only add columns which do not have the aforementioned types.
        :param seed: Random seed used for sampling the data.
            Values can be any integer between 0 and 2**32 - 1 inclusive or None.
        :param args: args for HasTraits superclass
        :param kwargs: kwargs for HasTraits superclass

        """
        super().__init__(*args, **kwargs)
        validate.validate_data_frame(df)
        validate.validate_sample(sample)
        validate.validate_seed(seed)

        self.selection_type = SelectionType.STANDARD
        if sample is None:
            self._df = df
        else:
            if isinstance(sample, float):
                if sample < 0.0 or sample > 1.0:
                    raise ValueError(
                        "Sample has to be between 0.0 and 1.0. Invalid value : %d"
                        % sample
                    )
                self._df = df.sample(frac=sample, random_state=seed)
            else:
                if sample < 0 or sample > len(df):
                    raise ValueError(
                        "Sample has to be between 0 and the length of the DataFrame (%d). Invalid value: "
                        "%d" % (len(df), sample)
                    )
                self._df = df.sample(n=sample, random_state=seed)
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
        self._indices = set(range(self._length))
        self._brushed_indices: typing.Set[int] = self._indices

        self.brushed_data_invalidated = True
        self._brushed_data = None

        self.on_indices_changed = Signal()

        if len(self.columns) < 2:
            raise ValueError(
                "The passed DataFrame only has %d column, which is insufficient for analysis."
                % len(self.columns)
            )

        self.few_num_cols = len(self.numerical_columns) < 2
        self.few_cat_cols = len(self.categorical_columns) < 2

    def notify_indices_changed(self):
        # This has the effect that the cached value for brushed_data is being re-indexed once it is needed.
        self.brushed_data_invalidated = True

        self.on_indices_changed.send(self)

    def reset_selection(self):
        """
        Reset all the indices to the original state, that is all indices are selected.

        :return: None
        """
        self._brushed_indices = self._indices
        self.notify_indices_changed()

    @property
    def len(self) -> int:
        """

        :return: The length of the DataFrame.
        """
        return self._length

    def __len__(self):
        """

        :return: The length of the DataFrame.
        """
        return self._length

    @property
    def brushed_indices(self) -> typing.Set[int]:
        """

        :return: The currently selected indices.
        """
        return self._brushed_indices

    @brushed_indices.setter
    def brushed_indices(self, indices: typing.List[int]):
        """
        Sets the specified indices as selection in the data according to the current selection type.

        :param indices: indices of data points that should be brushed.
        """
        if self.selection_type == SelectionType.STANDARD:
            self._brushed_indices = set(indices)
        elif self.selection_type == SelectionType.ADDITIVE:
            self._brushed_indices = self._brushed_indices.union(indices)
        elif self.selection_type == SelectionType.SUBTRACTIVE:
            self._brushed_indices = self._brushed_indices.difference(indices)

        self.notify_indices_changed()

    @property
    def brushed_data(self) -> DataFrame:
        """
        Only determines brushed data if it was invalidated by new selected indices.
        This gives more efficiency if only the brushed indices are needed and not the brushed data.

        :return: The selected data corresponding to the indices.
        """
        if self.brushed_data_invalidated:
            self._brushed_data = self._df.iloc[list(self._brushed_indices), :]
            self.brushed_data_invalidated = False
        return self._brushed_data

    @property
    def indices(self) -> typing.Set[int]:
        """

        :return: All indices of the data frame. This is a list from 0 to len-1.
        """
        return self._indices

    @property
    def data(self) -> DataFrame:
        """

        :return: The DataFrame for this :class:`pandas_visual_analysis.data_source.DataSource` object.
        """
        return self._df
