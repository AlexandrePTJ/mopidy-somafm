from __future__ import unicode_literals

import logging

from mopidy import backend

logger = logging.getLogger(__name__)


class SomaFMPlaylistsProvider(backend.PlaylistsProvider):

    def __init__(self, *args, **kwargs):
        super(SomaFMPlaylistsProvider, self).__init__(*args, **kwargs)

    def lookup(self, uri):
        for playlist in self.playlists:
            if playlist.uri == uri:
                return playlist

    def refresh(self):
        self.backend.somafm_client.refresh()
