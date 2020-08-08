from abc import abstractmethod

from traitlets import Instance, HasTraits
import ipywidgets as widgets

from pandas_visual_analysis import DataSource


class BaseWidget(HasTraits):

    data_source = Instance(DataSource)

    def __init__(self, data_source: DataSource, row: int, index: int, relative_size: float, max_height: int):
        """
        Instantiates the base class of the widgets.
        :param data_source: Every widget will observe changes to the changes in the DataSource.
        :param row: The row the widget is in.
        :param index: Index of the row the widget is in.
        :param relative_size: ratio of the row the widget is allowed to take up
        :param max_height: height in pixels the plot has to have
"""
        super().__init__()
        self.data_source = data_source
        self.row: int = row
        self.index: int = index
        self.relative_size = relative_size
        self.max_height = max_height

    @abstractmethod
    def build(self) -> widgets.Widget:
        """
        This method returns an IPython Widget containing all the children of the widget.
        """
        pass

    @abstractmethod
    def observe_brush_indices_change(self, change):
        """
        This method observes the changes in the brush selection.
        In order to actually observe changes it has to be registered in :meth:`set_observers`
        :param change: Value containing the new and old values that can be accessed with change['new'] or change['old'].
        """
        pass

    @abstractmethod
    def set_observers(self):
        """
        This method adds the necessary callbacks to trait changes.
        """
        pass

    @abstractmethod
    def on_selection(self, trace, points, state):
        """
        This method implements the behaviour of changes in the selection of this plot.
        Should set the brushed indices property of :class:`pandas_visual_analysis.data_source.DataSource` in order
        to propagate the change.
        :param trace:
        :param points:
        :param state:
        :return:
        """
        pass

    @abstractmethod
    def on_deselection(self, trace, points):
        """
        This method implements the behaviour of changes in the deselection of this plot.
        Should reset the brushed selection of :class:`pandas_visual_analysis.data_source.DataSource` in order
        to propagate the change.
        :param trace:
        :param points:
        """
        pass
