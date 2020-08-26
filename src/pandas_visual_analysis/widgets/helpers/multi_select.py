import typing

import ipywidgets as widgets
from traitlets import HasTraits, List


class HasMultiSelect:
    def __init__(self, columns, relative_size, max_height):
        self.columns: List[str] = columns
        self.selected_columns = columns

        self.select_threshold = int(15 * relative_size)
        self.use_multi_select = len(columns) > self.select_threshold

        if self.use_multi_select:
            self.show_multi_select = True
            self.multi_select: MultiSelectWidget = MultiSelectWidget(
                options=columns,
                selection=columns[0 : self.select_threshold],
                max_height=max_height,
            )
            self.multi_select_widget = self.multi_select.build()
            self.selected_columns = self.multi_select.selected_options
        else:
            self.show_multi_select = False
            self.multi_select_toggle = False
            self.multi_select = None


# inspired by: https://gist.github.com/MattJBritton/9dc26109acb4dfe17820cf72d82f1e6f
class MultiSelectWidget(HasTraits):

    selected_options = List()

    def __init__(
        self,
        options: typing.List[str],
        selection=None,
        relative_size: float = 0.3,
        max_height: typing.Optional[int] = 300,
    ):
        super().__init__()

        if selection is None:
            num = min(len(options), 5)
            selection = [options[i] for i in range(num)]

        if not set(selection).issubset(set(options)):
            raise ValueError("Selection can only contain values in options.")

        self.options = options
        self.max_height = max_height

        self.options_widgets = [
            widgets.Checkbox(
                description=option,
                value=option in selection,
                style={"description_width": "0px"},
                layout=widgets.Layout(
                    min_height="28px", max_width="90%"
                ),  # , max_width='%dpx' % (self.width - 20))
            )
            for i, option in enumerate(self.options)
        ]

        self.options_layout = widgets.Layout(
            overflow="auto",
            max_height="100%"
            if max_height is None
            else "%dpx" % (self.max_height - 100),
            flex_flow="column",
            display="flex",
        )

        self.deselect_all = widgets.Button(
            description="Deselect All", disabled=False, icon="times"
        )

        self.select_all = widgets.Button(
            description="Select All", disabled=False, icon="check"
        )

        self.info_label = widgets.Label(
            value="%d of %d selected" % (len(self.selected_options), len(self.options))
        )
        self.search_widget = widgets.Text(layout=widgets.Layout(max_width="80%"))

        self.options_widget = widgets.VBox(
            children=self.options_widgets, layout=self.options_layout
        )
        multi_select = widgets.VBox([self.search_widget, self.options_widget])
        buttons = widgets.HBox([self.select_all, self.deselect_all])

        self.selected_options = [
            option.description for option in self.options_widgets if option.value
        ]
        self.info_label.value = "%d of %d selected" % (
            len(self.selected_options),
            len(self.options),
        )

        self.root = widgets.VBox(
            [buttons, multi_select, self.info_label],
            layout=widgets.Layout(
                border="1px solid black",
                max_height="100%" if max_height is None else "%dpx" % self.max_height,
                display="block",
                max_width=str(relative_size * 100) + "%",
            ),
        )

        self.enable_selection_change = True
        for checkbox in self.options_widgets:
            checkbox.observe(self.on_checkbox_change, names="value")
        self.search_widget.observe(self.on_text_change, names="value")
        self.select_all.on_click(self.on_select_all)
        self.deselect_all.on_click(self.on_deselect_all)

    def build(self):
        return self.root

    def on_checkbox_change(self, change):
        selected_recipe = change["owner"].description
        checked = change["new"]
        if not self.enable_selection_change:
            return
        if checked:
            if selected_recipe not in self.selected_options:
                self.selected_options = self.selected_options + [selected_recipe]
        else:
            self.selected_options = [
                value for value in self.selected_options if value != selected_recipe
            ]
        self.info_label.value = "%d of %d selected" % (
            len(self.selected_options),
            len(self.options),
        )

    def on_text_change(self, change):
        search_input = change["new"]
        if search_input == "":
            # Reset search field
            # new_options = sorted(self.options_widgets, key=lambda x: x.value, reverse=True)
            new_options = self.options_widgets
        else:
            close_matches = [
                x
                for x in self.options
                if str.lower(search_input.strip("")) in str.lower(x)
            ]
            new_options = sorted(
                [x for x in self.options_widgets if x.description in close_matches],
                key=lambda x: x.value,
                reverse=True,
            )  # [options_dict[x] for x in close_matches]
        self.options_widget.children = new_options

    def on_select_all(self, b):
        self.enable_selection_change = False
        for checkbox in self.options_widgets:
            checkbox.value = True
        self.enable_selection_change = True
        self.selected_options = self.options

    def on_deselect_all(self, b):
        self.enable_selection_change = False
        for checkbox in self.options_widgets:
            checkbox.value = False
        self.enable_selection_change = True
        self.selected_options = []
