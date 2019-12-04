import logging
import pathlib

import pkg_resources

from mopidy import config, ext

__version__ = pkg_resources.get_distribution("Mopidy-SomaFM").version

logger = logging.getLogger(__name__)


class Extension(ext.Extension):

    dist_name = "Mopidy-SomaFM"
    ext_name = "somafm"
    version = __version__

    def get_default_config(self):
        return config.read(pathlib.Path(__file__).parent / "ext.conf")

    def get_config_schema(self):
        schema = super().get_config_schema()
        schema["encoding"] = config.String(choices=("aac", "mp3", "aacp"))
        schema["quality"] = config.String(
            choices=("highest", "fast", "slow", "firewall")
        )
        schema["dj_as_artist"] = config.Boolean()
        return schema

    def setup(self, registry):
        from .backend import SomaFMBackend

        registry.add("backend", SomaFMBackend)
