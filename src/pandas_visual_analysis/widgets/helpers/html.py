from ipywidgets import widgets

from pandas_visual_analysis.data_source import DataSource
from pandas_visual_analysis.widgets.base_widget import BaseWidget


class HTMLWidget:

    def __init__(self, content: str):
        self.html_content = content

    @property
    def content(self):
        return self.html_content

    @content.setter
    def content(self, html_content):
        self.html_content = html_content

    def build(self):
        return widgets.HTML(value=self.html_content)

    # brush changes don't need to be observed
    def observe_brush_indices_change(self, change):
        pass

    def observe_brush_data_change(self, change):
        pass

    def set_observers(self):
        pass
