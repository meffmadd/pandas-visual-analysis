import pytest

from pandas_visual_analysis.widgets.helpers.multi_select import MultiSelectWidget


@pytest.fixture(scope="module")
def sample_options():
    return ["Option" + str(i) for i in range(20)]


class TestInit:
    def test_object_creation_basic(self, sample_options):
        MultiSelectWidget(sample_options, sample_options[0:3], 0.3, 400)

    def test_init_no_selection(self, sample_options):
        ms = MultiSelectWidget(sample_options, None, 0.3, 400)
        assert len(ms.selected_options) != 0

    def test_init_wrong_selected_option(self, sample_options):
        with pytest.raises(ValueError):
            MultiSelectWidget(sample_options, ["Option3", "some Option"], 0.3, 400)


class TestCheckboxChange:
    def test_basic_change_add(self, sample_options):
        ms = MultiSelectWidget(sample_options, sample_options[0:5], 0.3, 400)
        change = {"owner": ms.options_widgets[5], "new": True}
        ms.on_checkbox_change(change)
        assert len(ms.selected_options) == 6

    def test_basic_change_remove(self, sample_options):
        ms = MultiSelectWidget(sample_options, sample_options[0:5], 0.3, 400)
        change = {"owner": ms.options_widgets[0], "new": False}
        ms.on_checkbox_change(change)
        assert len(ms.selected_options) == 4


class TestTextChange:
    def test_search(self, sample_options):
        ms = MultiSelectWidget(sample_options, sample_options[0:5], 0.3, 400)
        ms.search_widget.value = "3"
        assert len(ms.options_widget.children) == 2

        ms.search_widget.value = ""
        assert len(ms.options_widget.children) == len(sample_options)


class TestSelectUI:
    def test_select_all(self, sample_options):
        ms = MultiSelectWidget(sample_options, sample_options[0:5], 0.3, 400)
        ms.on_select_all(None)
        assert len(ms.selected_options) == len(sample_options)

    def test_deselect_all(self, sample_options):
        ms = MultiSelectWidget(sample_options, sample_options[0:5], 0.3, 400)
        ms.on_deselect_all(None)
        assert len(ms.selected_options) == 0
