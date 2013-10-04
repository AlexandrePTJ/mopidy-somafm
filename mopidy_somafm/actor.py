from __future__ import unicode_literals

import logging
import pykka

from mopidy.backends import base

from .playlists import SomaFMPlaylistsProvider
from .library import SomaFMLibraryProvider
from .playback import SomaFMPlaybackProvider
from .somafm import SomaFMClient

logger = logging.getLogger('mopidy.backends.somafm')


def format_proxy(scheme, username, password, hostname, port):
    if hostname:

        # scheme must exists, so if None is give, we set default to http
        if not scheme:
            scheme = "http"
        # idem with port, default at 80
        if not port:
            port = 80

        # with authentification
        if username and password:
            return "%s://%s:%s@%s:%i" % (scheme, username, password, hostname, port)
        # ... or without
        else:
            return "%s://%s:%i" % (scheme, hostname, port)

    else:
        return None



class SomaFMBackend(pykka.ThreadingActor, base.Backend):

    def __init__(self, config, audio):
        super(SomaFMBackend, self).__init__()
        self.config = config

        full_proxy = format_proxy(
            scheme=config['proxy']['scheme'],
            username=config['proxy']['username'],
            password=config['proxy']['password'],
            hostname=config['proxy']['hostname'],
            port=config['proxy']['port'])

        self.somafm_client = SomaFMClient(backend=self, proxy=full_proxy)
        self.library = SomaFMLibraryProvider(backend=self)
        self.playback = SomaFMPlaybackProvider(backend=self, audio=audio)
        self.playlists = SomaFMPlaylistsProvider(backend=self)

        self.uri_schemes = ['somafm']

    def on_start(self):
    	self.somafm_client.refresh()
