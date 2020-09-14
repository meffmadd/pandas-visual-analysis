from typing import List


class ColumnIterator:

    """
    Iterates over a list of strings and warps around if end of list is reached, thus returning the first element again.
    """

    def __init__(self, columns: List[str]):
        self.columns = columns
        self.index = 0

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self) -> str:
        self.index = self.index % len(self.columns)
        value = self.columns[self.index]
        self.index = (
            self.index + 1
        )  # split up because of possibility to check restart with index == len
        return value

    def __len__(self) -> int:
        return len(self.columns)


class ColumnStore:

    """
    Determines the different column types from a DataFrame and provides access to the columns.
    With the various 'next' methods, the column names can be iterated with the call returning a different element
    each time until the end is reached and the first column name is returned again.
    """

    def __init__(self, df, columns, categorical_columns):
        self._df = df
        self.columns = columns
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

        self.numerical_iterator = ColumnIterator(self.numerical_columns)
        self.categorical_iterator = ColumnIterator(self.categorical_columns)
        self.time_iterator = ColumnIterator(self.time_columns)

        self.prefer_numerical = ColumnIterator(
            self.numerical_columns + self.time_columns + self.categorical_columns
        )
        self.prefer_categorical = ColumnIterator(
            self.categorical_columns + self.time_columns + self.numerical_columns
        )
        self.prefer_time = ColumnIterator(
            self.time_columns + self.numerical_columns + self.categorical_columns
        )

    def next_numerical(self) -> str:
        """
        Iterates over the numerical columns and only returns numerical column names.

        :return: Name of the next numerical column.
        """
        return next(self.numerical_iterator)

    def next_categorical(self) -> str:
        """
        Iterates over the categorical columns and only returns categorical column names.

        :return: Name of the next categorical column.
        """
        return next(self.categorical_iterator)

    def next_time(self) -> str:
        """
        Iterates over the time based columns and only returns time based column names.

        :return: Name of the next time based column.
        """
        return next(self.time_iterator)

    def next_prefer_numerical(self):
        """
        Iterates over all columns but first returns the numerical column names, then the time based column names
        and finally the categorical columns.

        :return: Name of the next column.
        """
        return ColumnStore._next_prefer(
            self.numerical_iterator, self.time_iterator, self.categorical_iterator
        )

    def next_prefer_categorical(self):
        """
        Iterates over all columns but first returns the categorical column names, then the time based column names
        and finally the numerical columns.

        :return: Name of the next column.
        """
        return ColumnStore._next_prefer(
            self.categorical_iterator, self.time_iterator, self.numerical_iterator
        )

    def next_prefer_time(self):
        """
        Iterates over all columns but first returns the time based column names, then the numerical column names
        and finally the categorical columns.

        :return: Name of the next column.
        """
        return ColumnStore._next_prefer(
            self.time_iterator, self.numerical_iterator, self.categorical_iterator
        )

    @staticmethod
    def _next_prefer(
        it1: ColumnIterator, it2: ColumnIterator, it3: ColumnIterator
    ) -> str:
        """
        Return next name from iterator that is not at the end. If all are at the end, resets all iterators and
        starts again.

        :param it1: The iterator that should be used first.
        :param it2: The iterator that should be used second.
        :param it3: The iterator that should be used last.
        :return:
        """
        if it1.index != len(it1):
            return next(it1)
        elif it2.index != len(it2):
            return next(it2)
        elif it3.index != len(it3):
            return next(it3)
        else:
            it1.index = 0
            it2.index = 0
            it3.index = 0
            return next(it1)
