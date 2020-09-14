import time

import pytest

from pandas_visual_analysis.utils.util import (
    hex_to_rgb,
    compare_lists,
    timing,
    Timer,
    text_color,
)


def test_hex_to_rgb():
    assert hex_to_rgb("#ffffff") == (255, 255, 255)


def test_hex_to_rgb_uppercase():
    assert hex_to_rgb("#F245E1") == (242, 69, 225)


def test_hex_to_rgb_error_some_text():
    with pytest.raises(ValueError):
        hex_to_rgb("asdfefasdffe")


def test_hex_to_rgb_error_non_hex():
    with pytest.raises(ValueError):
        hex_to_rgb("#ff3X45")


def test_hex_to_rgb_error_non_hashtag():
    with pytest.raises(ValueError):
        hex_to_rgb("ffffff")


# noinspection PyTypeChecker
def test_hex_to_rgb_error_random_input():
    with pytest.raises(TypeError):
        hex_to_rgb(2)


# noinspection PyTypeChecker
def test_hex_to_rgb_error_none():
    with pytest.raises(TypeError):
        hex_to_rgb(None)


def test_compare_lists():
    assert compare_lists([1, 2, 2], [1, 2, 2]) is True


def test_compare_lists_neg():
    assert compare_lists([1, 2, 2], [1, 2, 4]) is False


def test_compare_lists_duplicates():
    assert compare_lists([4, 5], [4, 5, 5]) is False


def test_compare_lists_none():
    assert compare_lists([1, 4], None) is False


def test_compare_lists_some_value():
    assert compare_lists("str", [1, 4]) is False


def test_timing(capsys):
    @timing
    def to_time():
        time.sleep(1)

    to_time()
    captured = capsys.readouterr()
    string: str = captured.out
    assert "to_time" in string


def test_timer():
    timer = Timer()
    time.sleep(1)
    timer.stop()

    assert ((timer.end_time - timer.start_time) * 1000.0) > 1000.0  # ms


def test_text_color_white():
    col = text_color((255, 255, 255))
    assert col == (0, 0, 0)
