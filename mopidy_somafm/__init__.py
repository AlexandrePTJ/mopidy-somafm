from __future__ import unicode_literals

import os

from mopidy import config, exceptions, ext

__version__ = '0.1.1'

class Extension(ext.Extension):

    dist_name = 'Mopidy-SomaFM'
    ext_name = 'somafm'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        return schema

    def validate_environment(self):
        try:
            import requests
        except ImportError as e:
            raise ExtensionError('Library requests not found', e)

    def get_backend_classes(self):
        from .actor import SomaFMBackend
        return [SomaFMBackend]
