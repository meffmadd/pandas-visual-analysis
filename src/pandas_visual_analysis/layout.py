import typing

from ipywidgets import widgets

from pandas_visual_analysis.data_source import DataSource
from pandas_visual_analysis.widgets import BaseWidget
from pandas_visual_analysis.widgets.registry import WidgetClassRegistry
import pandas_visual_analysis.utils.validation as validate


class AnalysisLayout:
    """
    The AnalysisLayout class determines which widgets should be displayed in the analysis
    and defines their position and size.

    :param layout: the layout specification
    :param row_height: height in pixels each row and consequently each plot should have
    :param data_source: the :class:`pandas_visual_analysis.data_source.DataSource` object passed to the widgets
    """

    root_widget = None

    predefined_layouts = {
        "default": [["BrushSummary", "Scatter"], ["Histogram", "Scatter"]]
    }

    def __init__(
        self,
        layout: typing.Union[str, typing.List[typing.List[str]]],
        row_height: int,
        data_source: DataSource,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        validate.validate_row_height(row_height)
        if isinstance(layout, str):
            if layout not in set(self.predefined_layouts.keys()):
                raise ValueError(
                    "The specified layout is invalid. Only these values are accepted: %s"
                    % str(self.predefined_layouts.keys())
                )
            self.layout_spec = self.predefined_layouts[layout]
        elif isinstance(layout, list):
            self.layout_spec = layout
            valid_widgets = WidgetClassRegistry().widget_set

            if any([el not in valid_widgets for row in self.layout_spec for el in row]):
                raise ValueError(
                    "Some widget names are not valid. "
                    "Only the following widgets can be included in a layout specification: %s"
                    % (str(valid_widgets))
                )

        else:
            raise TypeError(
                "The layout specification either has to be a string or a list of list of strings."
            )

        self.data_source = data_source
        self.row_height = row_height

    def build(self) -> widgets.Widget:
        """
        Generates widgets from layout and returns the root widget for this layout.
        Rows are in a VBox while plots in the rows are in HBox widgets.
        :return: self.root_widget
        """
        wcr = WidgetClassRegistry()
        rows = []
        for r, row in enumerate(self.layout_spec):
            row_widgets = []
            for i, widget_name in enumerate(row):
                widget_cls: BaseWidget.__class__ = wcr.get_widget_class(widget_name)
                widget = widget_cls(
                    self.data_source, r, i, 1.0 / len(row), self.row_height
                )
                row_widgets.append(widget.build())
            h_box = widgets.HBox(row_widgets)
            rows.append(h_box)
        self.root_widget = widgets.VBox(rows)
        return self.root_widget
