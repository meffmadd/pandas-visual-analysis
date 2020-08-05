import typing
import ipywidgets as widgets
from traitlets import HasTraits, List, observe

from pandas_visual_analysis.utils import debounce


class MultiSelectWidget(HasTraits):

    selected_options = List()

    def __init__(self, options: typing.List[str], width: int = 200, max_height: int = 300):
        super().__init__()

        self.options = options
        self.width = width
        self.max_height = max_height

        self.options_widgets = [
            widgets.Checkbox(
                description=option,
                value=(i < 5),
                style={"description_width": "0px"},
                layout=widgets.Layout(min_height='28px', max_width='%dpx' % (self.width - 20))
            )
            for i, option in enumerate(self.options)
        ]

        self.options_layout = widgets.Layout(
            overflow='auto',
            max_width='%dpx' % self.width,
            max_height='100%' if max_height is None else '%dpx' % (self.max_height - 30),
            flex_flow='column',
            display='flex'
        )

        self.deselect_all = widgets.Button(
            description='Deselect All',
            disabled=False,
            icon='times'
        )

        self.select_all = widgets.Button(
            description='Select All',
            disabled=False,
            icon='check'
        )

        self.info_label = widgets.Label(value="%d of %d selected" % (len(self.selected_options), len(self.options)))
        search_widget = widgets.Text(layout=widgets.Layout(max_width='%dpx' % self.width))

        self.options_widget = widgets.VBox(children=self.options_widgets, layout=self.options_layout)
        multi_select = widgets.VBox([search_widget, self.options_widget])
        buttons = widgets.HBox([self.select_all, self.deselect_all],
                               layout=widgets.Layout(max_width='%dpx' % self.width))

        self.selected_options = [option.description for option in self.options_widgets if option.value]
        self.info_label.value = "%d of %d selected" % (len(self.selected_options), len(self.options))

        self.root = widgets.VBox([buttons, multi_select, self.info_label],
                                 layout=widgets.Layout(
                                     border='1px solid black',
                                     max_width='%dpx' % (self.width + 10),
                                     # max_height='%dpx' % self.max_height
                                 ))

        for checkbox in self.options_widgets:
            checkbox.observe(self.on_checkbox_change, names="value")
        search_widget.observe(self.on_text_change, names='value')
        self.select_all.on_click(self.on_select_all)
        self.deselect_all.on_click(self.on_deselect_all)

    def build(self):
        return self.root

    @debounce(0.2)
    def on_checkbox_change(self, change):
        selected_recipe = change["owner"].description

        checked = change['new']
        if checked:
            if selected_recipe not in self.selected_options:
                self.selected_options = self.selected_options + [selected_recipe]
        else:
            self.selected_options = [value for value in self.selected_options if value != selected_recipe]

        self.info_label.value = "%d of %d selected" % (len(self.selected_options), len(self.options))

    def on_text_change(self, change):
        search_input = change['new']
        if search_input == '':
            # Reset search field
            new_options = sorted(self.options_widgets, key=lambda x: x.value, reverse=True)
        else:
            # Filter by search field using difflib.
            # close_matches = difflib.get_close_matches(search_input, list(options_dict.keys()), cutoff=0.0)
            close_matches = [x for x in self.options if str.lower(search_input.strip('')) in str.lower(x)]
            new_options = sorted(
                [x for x in self.options_widgets if x.description in close_matches],
                key=lambda x: x.value, reverse=True
            )  # [options_dict[x] for x in close_matches]
        self.options_widget.children = new_options

    def on_select_all(self, b):
        for checkbox in self.options_widgets:
            checkbox.value = True
        self.selected_options = self.options

    def on_deselect_all(self, b):
        for checkbox in self.options_widgets:
            checkbox.value = False
        self.selected_options = []

