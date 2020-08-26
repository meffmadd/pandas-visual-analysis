import pytest

from pandas_visual_analysis.utils.config import Config


def test_config_store_and_get():
    config = Config()
    val = [1, 3]
    config["val"] = val
    assert config["val"] is val


def test_config_attributes():
    config = Config()
    val = "hello"
    config.val = val
    assert config.val is val


def test_config_attribute_error():
    config = Config()
    val = "hello"
    with pytest.raises(ValueError):
        config.keys = val


def test_config_singleton():
    config1 = Config()
    config2 = Config()
    assert config1 is config2
