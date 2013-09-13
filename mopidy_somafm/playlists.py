from __future__ import unicode_literals

import logging

from mopidy.backends import base, listener
from mopidy.models import Playlist

logger = logging.getLogger('mopidy.backends.somafm')


class SomaFMPlaylistsProvider(base.BasePlaylistsProvider):

    def __init__(self, *args, **kwargs):
        super(SomaFMPlaylistsProvider, self).__init__(*args, **kwargs)
        self.refresh()

    def create(self, name):
        # Not applicable
        pass

    def delete(self, uri):
        # Not applicable
        pass

    def lookup(self, uri):
        for playlist in self.backend.somafm_client.playlists:
            if playlist.uri == uri:
                return playlist
        return None

    def refresh(self):
        self.backend.somafm_client.refresh()
        self.playlists = self.backend.somafm_client.playlists
        logger.info('Loaded %s SomaFM playlist(s)', len(self.playlists))
        listener.BackendListener.send('playlists_loaded')

    def save(self, playlist):
        # Not applicable
        pass
