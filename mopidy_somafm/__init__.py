from __future__ import unicode_literals

import os

from mopidy import config, ext

__version__ = '0.7.0'


class Extension(ext.Extension):

    dist_name = 'Mopidy-SomaFM'
    ext_name = 'somafm'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema['encoding'] = config.String(choices=('aac', 'mp3'))
        schema['quality'] = config.String(
            choices=('highest', 'fast', 'slow', 'firewall'))
        return schema

    def validate_environment(self):
        pass

    def setup(self, registry):
        from .actor import SomaFMBackend
        registry.add('backend', SomaFMBackend)
