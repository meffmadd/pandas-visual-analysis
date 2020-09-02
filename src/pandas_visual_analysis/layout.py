import typing
import uuid

from ipywidgets import widgets

from pandas_visual_analysis.data_source import DataSource, SelectionType
from pandas_visual_analysis.utils.config import Config
from pandas_visual_analysis.widgets import BaseWidget
from pandas_visual_analysis.widgets.registry import WidgetClassRegistry
from pandas_visual_analysis.utils.util import text_color
import pandas_visual_analysis.utils.validation as validate


class AnalysisLayout:
    """
    The AnalysisLayout class determines which widgets should be displayed in the analysis
    and defines their position and size.
    """

    root_widget = None

    predefined_layouts = {
        "default": [["BrushSummary", "Scatter"], ["Histogram", "Scatter"]]
    }

    def __init__(
        self,
        layout: typing.Union[str, typing.List[typing.List[str]]],
        row_height: typing.Union[int, typing.List[int]],
        data_source: DataSource,
        *args,
        **kwargs
    ):
        """

        :param layout: Layout specification name or explicit definition of widget names in rows.
        :param row_height: Height in pixels each row should have. If given an integer, each row has the height
            specified by that value, if given a list of integers, each value in the list specifies the height of
            the corresponding row.
        :param data_source: The :class:`pandas_visual_analysis.data_source.DataSource` object passed to the widgets
            in that layout.
        """
        super().__init__(*args, **kwargs)
        self._id = uuid.uuid4().hex

        if isinstance(layout, str):
            if layout not in set(self.predefined_layouts.keys()):
                raise ValueError(
                    "The specified layout is invalid. Only these values are accepted: %s"
                    % str(self.predefined_layouts.keys())
                )
            self.layout_spec = self.predefined_layouts[layout]
        elif (
            isinstance(layout, list)
            and all(isinstance(x, list) for x in layout)
            and all(isinstance(x, str) for row in layout for x in row)
        ):
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

        validate.validate_row_height(row_height, self.layout_spec)

        self.data_source = data_source
        self.row_height = row_height
        self.selection_type_widget = widgets.ToggleButtons(
            options=[("Standard", "std"), ("Additive", "add"), ("Subtractive", "sub")],
            description="Selection Type:",
            disabled=False,
            button_style="",  # 'success', 'info', 'warning', 'danger' or ''
            tooltips=[
                "Replaces selection",
                "Adds selected points to selection",
                "Removes selected points from selection",
            ],
            style={"description_width": "initial"},
        )
        self.selection_type_widget.add_class("layout-" + self._id)
        self.selection_type_widget.observe(self._selection_type_changed, "value")

    def build(self) -> widgets.Widget:
        """
        Generates widgets from layout and returns the root widget for this layout.
        Rows are in a VBox while plots in the rows are in HBox widgets.

        :return: self.root_widget
        """
        wcr = WidgetClassRegistry()
        rows = [self.selection_type_widget]  # first row is the selection type widget
        for r, row in enumerate(self.layout_spec):
            row_widgets = []
            if isinstance(self.row_height, int):
                current_row_height = self.row_height
            else:  # list
                current_row_height = self.row_height[r]
            for i, widget_name in enumerate(row):
                widget_cls: BaseWidget.__class__ = wcr.get_widget_class(widget_name)
                widget = widget_cls(
                    self.data_source, r, i, 1.0 / len(row), current_row_height
                )
                row_widgets.append(widget.build())
            h_box = widgets.HBox(row_widgets)
            rows.append(h_box)

        # workaround to include arbitrary css
        bg_color: typing.Tuple[int, int, int] = Config().select_color
        css = "<style>"
        css += ".jupyter-widgets { border-radius : 5px ; }"
        css += ".layout-{} * .jupyter-button.mod-active {{ background-color : rgb{}; color: rgb{}; }}".format(
            self._id, bg_color, text_color(bg_color)
        )  # add layout-xxx... class to buttons since this color is specific to this layout
        css += ".jupyter.button, .widget-toggle-button {border-radius : 5px; }"
        css += ".widget-dropdown > select {border-radius : 5px; }"
        css += (
            ".jupyter-widgets::-webkit-scrollbar-track { border-radius: 4px; background-color: #F5F5F5; "
            "-webkit-box-shadow: inset 0 0 6px rgba(0,0,0,0.15); }"
        )
        css += ".jupyter-widgets::-webkit-scrollbar { width: 7px; background-color: #F5F5F5; }"
        css += ".jupyter-widgets::-webkit-scrollbar-thumb {{ border-radius: 4px; background-color: rgb{col}; }}".format(
            col=(170, 170, 170)
        )
        css += "</style>"
        rows.append(widgets.HTML(css))

        self.root_widget = widgets.VBox(
            rows, layout=widgets.Layout(margin="20px 0px 10px 0px")
        )
        return self.root_widget

    def _selection_type_changed(self, change):
        value = change["new"]
        if value == "std":
            self.data_source.selection_type = SelectionType.STANDARD
        elif value == "add":
            self.data_source.selection_type = SelectionType.ADDITIVE
        elif value == "sub":
            self.data_source.selection_type = SelectionType.SUBTRACTIVE
