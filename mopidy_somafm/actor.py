from __future__ import unicode_literals

import logging
import pykka

from mopidy import backend

from .playlists import SomaFMPlaylistsProvider
from .library import SomaFMLibraryProvider
from .somafm import SomaFMClient

logger = logging.getLogger(__name__)


def format_proxy(scheme, username, password, hostname, port):
    """Format Proxy URL"""
    if hostname:
        # scheme must exists, so if None is give, we set default to http
        if not scheme:
            scheme = "http"
        # idem with port, default at 80
        if not port:
            port = 80
        # with authentification
        if username and password:
            return "%s://%s:%s@%s:%i" % (
                scheme, username, password, hostname, port)
        # ... or without
        else:
            return "%s://%s:%i" % (scheme, hostname, port)
    else:
        return None


class SomaFMBackend(pykka.ThreadingActor, backend.Backend):

    def __init__(self, config, audio):
        super(SomaFMBackend, self).__init__()

        full_proxy = format_proxy(
            scheme=config['proxy']['scheme'],
            username=config['proxy']['username'],
            password=config['proxy']['password'],
            hostname=config['proxy']['hostname'],
            port=config['proxy']['port'])

        self.somafm_client = SomaFMClient(backend=self, proxy=full_proxy)
        self.library = SomaFMLibraryProvider(backend=self)
        self.playlists = SomaFMPlaylistsProvider(backend=self)
        self.playback = None

        self.uri_schemes = ['somafm']

    def on_start(self):
        self.playlists.refresh()

    def on_stop(self):
        pass
