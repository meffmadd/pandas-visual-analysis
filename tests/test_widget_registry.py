import pytest

# from pandas_visual_analysis.widgets.base_widget import BaseWidget
from pandas_visual_analysis import VisualAnalysis
from pandas_visual_analysis.widgets.registry import WidgetClassRegistry, register_widget
from tests import sample_dataframes


@pytest.fixture
def empty_registry():
    old_registry = WidgetClassRegistry().registry
    WidgetClassRegistry().registry = {}
    yield WidgetClassRegistry()
    WidgetClassRegistry().registry = old_registry


def test_widget_class_registry_basic(empty_registry):
    wcr = empty_registry

    @register_widget
    class Test1Widget(object):
        pass

    assert wcr.has_widget("Test1")


def test_widget_class_registry_list_and_set(empty_registry):
    wcr = empty_registry

    @register_widget
    class Test1Widget(object):
        pass

    @register_widget
    class Test2Widget(object):
        pass

    assert wcr.widget_list == ["Test1", "Test2"]
    assert wcr.widget_set == {"Test1", "Test2"}


def test_widget_class_registry_singelton():
    wcr1 = WidgetClassRegistry()
    wcr2 = WidgetClassRegistry()
    assert wcr1 is wcr2


def test_widget_class_registry_get_class(empty_registry):
    wcr = empty_registry

    @register_widget
    class Test1Widget(object):
        pass

    obj = wcr.get_widget_class("Test1")()
    obj_normal = Test1Widget()

    assert obj.__class__ == obj_normal.__class__


def test_widget_class_registry_normal_behaviour():
    small_df = sample_dataframes.small_df()
    VisualAnalysis(small_df)
    assert len(WidgetClassRegistry().widget_list) > 0


def test_widget_class_registry_no_widget_end(empty_registry):
    wcr = empty_registry

    class Test1(object):
        pass

    with pytest.raises(ValueError):
        wcr.add(Test1)
