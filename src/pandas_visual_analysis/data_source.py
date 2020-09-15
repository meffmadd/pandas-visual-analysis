import os
import typing
from enum import Enum
from blinker import Signal
from pandas import DataFrame
import pandas as pd

import pandas_visual_analysis.utils.validation as validate
from pandas_visual_analysis.utils.column_store import ColumnStore


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

        self.column_store = ColumnStore(self._df, self.columns, categorical_columns)
        self.numerical_columns = self.column_store.numerical_columns
        self.time_columns = self.column_store.time_columns
        self.categorical_columns = self.column_store.categorical_columns

        if self.categorical_columns is not None:
            self._df[self.categorical_columns].astype(dtype="category")

        self._length = len(self._df)
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

    @staticmethod
    def read_csv(path: str, header: typing.Union[int, None] = 0):
        """
        Read a comma-separated values (csv) file into DataSource.

        :param path: Any valid string path is acceptable. The string could be a URL.
            Valid URL schemes include http, ftp, s3, and file.
        :param header: Row (0-indexed) to use for the column labels of the parsed DataFrame.
            Use None if there is no header.
        :return: The DataSource containing the data from the specified file.
        """
        df = pd.read_csv(path, header=header)
        return DataSource(df)

    @staticmethod
    def read_tsv(path: str, header: typing.Union[int, None] = 0):
        """
        Read a tab-separated values (tsv) file into DataSource.

        :param path: Any valid string path is acceptable. The string could be a URL.
            Valid URL schemes include http, ftp, s3, and file.
        :param header: Row (0-indexed) to use for the column labels of the parsed DataFrame.
            Use None if there is no header.
        :return: The DataSource containing the data from the specified file.
        """
        df = pd.read_table(path, header=header)
        return DataSource(df)

    @staticmethod
    def read_json(path: str, orient: str):
        """
         Read a json file into a DataSource.

        :param path: Any valid string path is acceptable. The string could be a URL.
            Valid URL schemes include http, ftp, s3, and file.
        :param orient: Indication of expected JSON string format produced by DataFrame.to_json()
            with a corresponding orient value.
        :return: The DataSource containing the data from the specified file.
        """
        df = pd.read_json(path, orient=orient)
        return DataSource(df)

    @staticmethod
    def read(path: str, *args, **kwargs):
        """
        Reads the data specified by the path into a DataSource. Infers file type by extension.
        Supported extensions are: .csv, .tsv and .json.

        :param path: Any valid string path is acceptable. The string could be a URL.
            Valid URL schemes include http, ftp, s3, and file.
        :param args: Arguments passed to inferred methods.
        :param kwargs: Keyword arguments passed to inferred methods.
        :return: The DataSource containing the data from the specified file.
        """
        filename, extension = os.path.splitext(path)
        supported_extensions = {".csv", ".tsv", ".json"}
        if extension not in supported_extensions:
            raise ValueError(
                "The file extension %s is not supported. "
                "Supported extensions are: .csv, .tsv, .json. "
            )

        if extension == ".csv":
            return DataSource.read_csv(path, *args, **kwargs)
        elif extension == ".tsv":
            return DataSource.read_tsv(path, *args, **kwargs)
        elif extension == ".json":
            return DataSource.read_json(path, *args, **kwargs)

    #  context manager
    def __enter__(self):
        """
        Enters the context.

        :return: Returns self to use as a resource.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exits the context. No resources have to be freed and all Exceptions are delegated.

        :param exc_type: Type of any raised Exception.
        :param exc_value: Value of any raised Exception.
        :param traceback: Traceback if an error occurred.
        :return: None
        """
        pass  # delegate Exceptions
