from abc import ABC, abstractmethod

from pandas_visual_analysis import DataSource


class BaseWidget(ABC):

    def __init__(self, data_source: DataSource, row: int, index: int):
        self.layout: DataSource = data_source
        self.row: int = row
        self.index: int = index

    @property
    def root(self):
        return self.root

    @abstractmethod
    def build(self):
        pass

    @abstractmethod
    def observe_brush_indices_change(self, change):
        """
        This method observes the changes in the brush selection.
        In order to actually observe changes it has to be decorated with
        '@observe(self.layout.data_source._brushed_indices)'
        If not needed do not implement and do not decorate.
        :param change: Value containing the new and old values that can be accessed with change['new'] or change['old'].
        """
        pass

    @abstractmethod
    def observe_brush_data_change(self, change):
        """
        This method observes the changes in the selected data from the brush selection.
        In order to actually observe changes it has to be decorated with
        '@observe(self.layout.data_source._brushed_data)'
        If not needed do not implement and do not decorate.
        :param change: Value containing the new and old values that can be accessed with change['new'] or change['old'].
        """
        pass


