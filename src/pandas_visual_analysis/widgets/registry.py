from typing import Set, List

from pandas_visual_analysis.utils.util import Singleton


class WidgetClassRegistry(object, metaclass=Singleton):
    def __init__(self):
        self.registry = {}

    @property
    def widget_set(self) -> Set[str]:
        """

        :return: Returns the set of names of all widgets registered in this object.
        """
        return set(self.registry.keys())

    @property
    def widget_list(self) -> List[str]:
        """

        :return: Returns the list of names of all widgets registered in this object.
        """
        return list(self.registry.keys())

    def has_widget(self, name: str) -> bool:
        """
        Checks if a widget has been registered by name.

        :param name: Class name of the widget.
        :return: Returns True iff the widget name is contained in the registry, False otherwise.
        """
        return name in self.registry

    def get_widget_class(self, name: str):
        """
        Gets the class of a widget that has been registered.

        :param name: Class name of the widget without the 'Widget'-suffix.
        :raises KeyError: if the name was not registered.
        :return: Returns the class of the widget.
        """
        return self.registry[name]

    def add(self, cls):
        """
        Adds a widget to the registry.
        The class has to end with 'Widget' in order to be registered, which is then removed from the name.
        This means 'TestWidget' will be registered as 'Test'.

        :param cls: Widget to add.
        :raises ValueError: if class name does not end with 'Widget'
        """
        if not cls.__name__.endswith("Widget"):
            raise ValueError(
                "Incorrect class name. Class has to end with 'Widget' in order to be registered."
            )
        name = cls.__name__[:-6]
        self.registry[name] = cls


def register_widget(cls):
    """
    Class decorator to add a widget class to the widget registry.

    :param cls: The class to add. The class name has to end in 'Widget'
    :return: The widget class.
    """
    WidgetClassRegistry().add(cls)
    return cls
