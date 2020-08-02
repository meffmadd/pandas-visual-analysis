from pandas_visual_analysis.data_source import DataSource
from pandas_visual_analysis.widgets.base_widget import BaseWidget
from ipywidgets import widgets


class HTMLWidget(BaseWidget):

    def __init__(self, data_source: DataSource, row: int, index: int):
        super().__init__(data_source, row, index)
        self.html_content = ""

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
