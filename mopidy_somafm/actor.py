from __future__ import unicode_literals

import logging
import pykka

from mopidy.backends import base

from .playlists import SomaFMPlaylistsProvider

logger = logging.getLogger('mopidy.backends.somafm')


class SomaFMBackend(pykka.ThreadingActor, base.Backend):

    def __init__(self, config, audio):
        super(SomaFMBackend, self).__init__()
        self.config = config
        self.library = None
        self.playback = None
        self.playlists = SomaFMPlaylistsProvider(backend=self)

        self.uri_schemes = ['somafm']
