import math

import ipywidgets as widgets
from traitlets import HasTraits

from pandas_visual_analysis import DataSource
from pandas_visual_analysis.widgets import BaseWidget, register_widget


@register_widget
class BrushSummaryWidget(BaseWidget):
    """
    The BrushSummaryWidget displays how a metric changes for the selection compared to the whole data.
    It shows all of the data as the baseline and displays the change in absolute values and as a percentage value.
    In addition it also displays arrows indicating the change with both color and direction.
    The magnitude of the change is illustrated as the size of the arrow to see the sensitivity at a glance.

    :param data_source: :class:`pandas_visual_analysis.data_source.DataSource` for the widget.
    :param row: The row the widget is in.
    :param index: Index of the row the widget is in.
    :param relative_size: The space the widget has in a row which is then converted to the width. (e.g. 0.33 => 33%)
    :param max_height: height in pixels the plot has to have
    """

    def __init__(
        self,
        data_source: DataSource,
        row: int,
        index: int,
        relative_size: float,
        max_height: int,
    ):
        super().__init__(data_source, row, index, relative_size, max_height)

        self.columns = (
            self.data_source.numerical_columns
        )  # + self.data_source.time_columns
        if len(self.columns) < 1:
            raise ValueError(
                "The data contains too few numerical columns to display the brush summary."
                "Remove the widget from the layout!"
            )

        self.metric_select = widgets.Dropdown(
            options=[
                ("Mean", "mean"),
                ("Minimum", "min"),
                ("1st Quartile", "25%"),
                ("Median", "50%"),
                ("3rd Quartile", "75%"),
                ("Maximum", "max"),
            ],
            value="mean",
            description="Metric:",
        )

        # grid columns: | column_name | data metric | brushed_data metric | indicator
        self.num_grid_columns = 4
        self.num_grid_rows = len(self.columns) + 1  # + 1 for count
        self.grid = widgets.GridspecLayout(self.num_grid_rows, self.num_grid_columns)

        self.base_metrics = self.data_source.data[self.columns].describe(include="all")
        self.brushed_metrics = self._get_brushed_metrics()

        self.pos_change_color = "red"
        self.neg_change_color = "green"
        self.item_layout = widgets.Layout(height="auto", width="auto")

        self._fill_empty_grid()
        self._update_column_names()
        self._update_base_metrics()
        self._update_brushed_metrics()

        self.metric_select.observe(self._observe_metric_change, names="value")
        self.set_observers()

    def build(self) -> widgets.Widget:
        root = widgets.VBox(
            [self.metric_select, self.grid], layout=widgets.Layout(overflow="auto")
        )
        return self.apply_size_constraints(root)

    def observe_brush_indices_change(self, change):
        self.brushed_metrics = self._get_brushed_metrics()
        self._update_brushed_metrics()

    def set_observers(self):
        # self.data_source.update.connect(receiver=self.observe_brush_indices_change)
        # self.data_source.observe_change(self.observe_brush_indices_change)
        HasTraits.observe(
            self.data_source,
            handler=self.observe_brush_indices_change,
            names="_brushed_indices",
        )

    def _observe_metric_change(self, obj):
        self._update_base_metrics()
        self._update_brushed_metrics()

    def on_selection(self, trace, points, state):
        pass

    def on_deselection(self, trace, points):
        pass

    def _fill_empty_grid(self):
        with self.grid.hold_trait_notifications():
            for i in range(self.num_grid_rows):
                for j in range(self.num_grid_columns):
                    self.grid[i, j] = widgets.HTML("")

    def _update_brushed_metrics(self):
        metric = self.metric_select.value
        brush_count = int(self.brushed_metrics.iloc[:, 0]["count"])
        with self.grid.hold_trait_notifications():
            self.grid[0, 2].value = self._get_metric_html_content(
                brush_count, brush_count / self.data_source.len - 1
            )

            for i, col in enumerate(self.columns):
                metric_value = self.brushed_metrics[col][metric]
                metric_base = self.base_metrics[col][metric]
                diff = metric_value / metric_base - 1
                self.grid[(i + 1), 2].value = self._get_metric_html_content(
                    metric_value, diff
                )
                self.grid[(i + 1), 3].value = self._get_indicator_html_content(diff)

    def _update_base_metrics(self):
        metric = self.metric_select.value

        with self.grid.hold_trait_notifications():
            self.grid[0, 1].value = self._get_metric_html_content(
                self.data_source.len, None
            )
            self.grid[0, 3].value = ""

            for i, col in enumerate(self.columns):
                self.grid[(i + 1), 1].value = self._get_metric_html_content(
                    self.base_metrics[col][metric]
                )

    def _update_column_names(self):
        with self.grid.hold_trait_notifications():
            self.grid[0, 0].value = "<b>Count</b>"
            for i, col in enumerate(self.columns):
                self.grid[(i + 1), 0].value = "<b>%s</b>" % col

    def _get_metric_html_content(self, metric_value: float, diff: float = None) -> str:
        percentage = "100%" if not diff else "{:.2%}".format((1 + diff))
        color = (
            "black"
            if not diff
            else self.pos_change_color
            if diff <= 0
            else self.neg_change_color
        )
        content = (
            '<p style="margin-bottom:-10px;color:%s">%s</p>'
            '<p style="margin-bottom:-10px;color:%s">%.4f</p>'
            % (color, percentage, color, metric_value)
        )
        return content

    def _get_indicator_html_content(self, diff: float) -> str:
        path = "M24 22h-24l12-20z" if diff > 0 else "M12 21l-12-18h24z"
        size = int(BrushSummaryWidget._map_value(abs(diff), -0.5, 0.5, 4, 20))
        color = self.pos_change_color if diff <= 0 else self.neg_change_color
        content = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 24 24" '
            'fill="%s"><path d="%s"/></svg>' % (size, size, color, path)
        )
        return content

    @staticmethod
    def _map_value(value, value_min, value_max, target_min, target_max) -> float:
        # Figure out how 'wide' each range is
        value = max(value, value_min)
        value = min(value, value_max)
        value_span = value_max - value_min
        target_span = target_max - target_min

        # Convert the left range into a 0-1 range (float)
        value_scaled = float(value - value_min) / float(value_span)

        # Convert the 0-1 range into a value in the right range.
        result = target_min + (value_scaled * target_span)
        if math.isnan(result):
            result = target_min
        return result

    def _get_brushed_metrics(self):
        return self.data_source.brushed_data[self.columns].describe(include="all")
