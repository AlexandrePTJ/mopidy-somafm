from mopidy_somafm import Extension


def test_get_default_config() -> None:
    ext = Extension()

    config = ext.get_default_config()

    assert "[somafm]" in config
    assert "enabled = true" in config


def test_get_config_schema() -> None:
    ext = Extension()

    schema = ext.get_config_schema()

    assert "encoding" in schema
    assert "quality" in schema


# TODO Write more tests
