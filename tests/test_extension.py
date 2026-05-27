from mopidy_somafm import Extension
from mopidy_somafm import backend as backend_lib


def test_get_default_config() -> None:
    ext = Extension()

    config = ext.get_default_config()

    assert "[somafm]" in config
    assert "enabled = true" in config


def test_get_config_schema() -> None:
    ext = Extension()

    schema = ext.get_config_schema()

    # TODO Test the content of your config schema
    # assert "username" in schema
    # assert "password" in schema


# TODO Write more tests
