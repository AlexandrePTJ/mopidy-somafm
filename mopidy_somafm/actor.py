from __future__ import unicode_literals

import logging
import pykka

from mopidy.backends import base

from .playlists import SomaFMPlaylistsProvider
from .library import SomaFMLibraryProvider
from .playback import SomaFMPlaybackProvider
from .somafm import SomaFMClient

logger = logging.getLogger('mopidy.backends.somafm')


class SomaFMBackend(pykka.ThreadingActor, base.Backend):

    def __init__(self, config, audio):
        super(SomaFMBackend, self).__init__()
        self.config = config
        self.somafm_client = SomaFMClient(backend=self)
        self.library = SomaFMLibraryProvider(backend=self)
        self.playback = SomaFMPlaybackProvider(backend=self, audio=audio)
        self.playlists = SomaFMPlaylistsProvider(backend=self)

        self.uri_schemes = ['somafm']

    def on_start(self):
    	self.somafm_client.refresh()
