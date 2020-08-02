import typing

from ipywidgets import widgets

from pandas_visual_analysis.data_source import DataSource
from pandas_visual_analysis.widgets.registry import WidgetClassRegistry


class AnalysisLayout:

    root_widget = None

    predefined_layouts = {
        "default": [[]]
    }

    def __init__(self, layout: typing.Union[str, typing.List[typing.List[str]]],
                 data_source: DataSource,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        if isinstance(layout, str):
            if layout not in set(self.predefined_layouts.keys()):
                raise ValueError("The specified layout is invalid. Only these values are accepted: %s"
                                 % str(self.predefined_layouts.keys()))
            self.layout_spec = self.predefined_layouts[layout]
        elif isinstance(layout, list):
            # todo: check if strings in the list of lists are valid widget names
            self.layout_spec = layout
            valid_widgets = WidgetClassRegistry().widget_set
            for row in self.layout_spec:
                for el in row:
                    if el not in valid_widgets:
                        raise ValueError("The widget name '%s' is not valid. "
                                         "Only the following widgets can be included in a layout specification: %s" %
                                         (el, str(valid_widgets)))
        else:
            raise TypeError("The layout specification either has to be a string or a list of list of strings.")

        self.data_source = data_source

    def build(self) -> widgets.Widget:
        self.root_widget = widgets.VBox()
        # todo: add widgets to root widget based on self.layout_spec
        return self.root_widget


