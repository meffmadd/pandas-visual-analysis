from collections import Counter
from typing import Tuple


def hex_to_rgb(hex_value: str) -> Tuple[int, int, int]:
    """
    Converts a valid hexadecimal color string given by '#XXXXXX' to a tuple representing RGB values.
    If the string representation does not match the above description, a ValueError is raised.
    :param hex_value: String representation of hexadecimal color.
    :return: Tuple of RGB color values: (R,G,B)
    """
    if len(hex_value) != 7 or hex_value[0] != '#':
        raise ValueError("the color has to be specified by '#XXXXXX'. Invalid value %s" % hex_value)
    hex_value = hex_value.lstrip('#')
    try:
        int(hex_value, 16)
    except ValueError:
        raise ValueError("the color value has to be a valid hexadecimal number. Invalid value %s" % hex_value)
    return int(hex_value[0:2], 16), int(hex_value[2:4], 16), int(hex_value[4:6], 16)


def compare_lists(s, t):
    """
    Compares two unordered lists and checks for equality.
    Duplicates are considered and False is returned when one list has a different number of the same item.
    The objects in the list have to be hashable.
    :param s: The first list to compare.
    :param t: The second list to compare.
    :return: True iff the two lists contain the same elements (including duplicates) in some order, False otherwise.
    """
    if not isinstance(s, list) or not isinstance(t, list):
        return False
    return len(s) == len(t) and Counter(s) == Counter(t)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

