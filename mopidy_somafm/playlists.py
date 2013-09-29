from __future__ import unicode_literals

import logging

from mopidy.backends import base
from mopidy.models import Playlist

logger = logging.getLogger('mopidy.backends.somafm')


class SomaFMPlaylistsProvider(base.BasePlaylistsProvider):

    def __init__(self, *args, **kwargs):
        super(SomaFMPlaylistsProvider, self).__init__(*args, **kwargs)

    def lookup(self, uri):
        for playlist in self.playlists:
            if playlist.uri == uri:
                return playlist

    def refresh(self):
        self.backend.somafm_client.refresh()
