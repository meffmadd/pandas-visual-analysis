from abc import abstractmethod

from traitlets import Instance, HasTraits
import ipywidgets as widgets

from pandas_visual_analysis import DataSource
from pandas_visual_analysis.utils.config import Config


class BaseWidget(HasTraits):

    data_source = Instance(DataSource)

    def __init__(
        self,
        data_source: DataSource,
        row: int,
        index: int,
        relative_size: float,
        max_height: int,
        *args,
        **kwargs
    ):
        """
        Instantiates the base class of the widgets.

        :param data_source: Every widget will observe changes to the changes in the DataSource.
        :param row: The row the widget is in.
        :param index: Index of the row the widget is in.
        :param relative_size: ratio of the row the widget is allowed to take up
        :param max_height: height in pixels the plot has to have
        """
        super().__init__(*args, **kwargs)
        self.data_source = data_source
        self.row: int = row
        self.index: int = index
        self.relative_size = relative_size
        self.max_height = max_height

    @abstractmethod
    def build(self) -> widgets.Widget:
        """
        This method returns an IPython Widget root node containing all the children for this widget.
        """
        pass

    def apply_size_constraints(self, widget):
        """
        Adds styling to a widget to control the height, width, margin, padding and border.
        Sets min and max_width to conform to the relative size of the widget, minus the margin.
        Sets min and max_width to conform to the max_height parameter.
        Adds a margin to the widget and also a padding with the same size.

        :param widget: An IPython widget to which the layout should be applied.
        :return: The same widget with updated layout.
        """
        with widget.hold_trait_notifications():
            margin = 5
            num_widgets_in_row = int(round(1 / self.relative_size)) - 1
            size_mod = (
                2 * num_widgets_in_row
            )  # because a border is added to each widget we have to subtract that (2px)
            widget.layout.min_width = (
                "calc("
                + str(self.relative_size * 100)
                + "%"
                + " - %dpx)" % (margin + size_mod)
            )
            widget.layout.max_width = (
                "calc("
                + str(self.relative_size * 100)
                + "%"
                + " - %dpx)" % (margin + size_mod)
            )
            widget.layout.max_height = "%dpx" % self.max_height
            widget.layout.min_height = "%dpx" % self.max_height
            widget.layout.margin = "%dpx %dpx %dpx %dpx" % (
                margin,
                margin,
                margin,
                margin,
            )
            widget.layout.padding = "%dpx %dpx %dpx %dpx" % (
                margin,
                margin,
                margin,
                margin,
            )
            widget.layout.border = "2px solid rgb(%d,%d,%d)" % Config().select_color
        return widget

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

        :param trace: The trace object which triggered the selection.
        :param points: The object containing the points in the 'point_inds' field.
        :param state: State of the input device.
        """
        pass

    @abstractmethod
    def on_deselection(self, trace, points):
        """
        This method implements the behaviour of changes in the deselection of this plot.
        Should reset the brushed selection of :class:`pandas_visual_analysis.data_source.DataSource` in order
        to propagate the change.

        :param trace: The trace object which triggered the deselection.
        :param points: The object containing the points in the 'point_inds' field.
        """
        pass
