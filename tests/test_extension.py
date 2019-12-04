from mopidy_somafm import Extension


def test_get_default_config():
    ext = Extension()

    config = ext.get_default_config()

    assert "[somafm]" in config
    assert "enabled = true" in config


def test_get_config_schema():
    ext = Extension()

    schema = ext.get_config_schema()

    assert "quality" in schema
    assert "encoding" in schema
