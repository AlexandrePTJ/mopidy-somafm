from __future__ import unicode_literals

import logging

from mopidy import backend
from mopidy.models import Playlist

logger = logging.getLogger(__name__)


class SomaFMPlaylistsProvider(backend.PlaylistsProvider):

    def create(self, name):
        pass

    def delete(self, name):
        pass

    def lookup(self, uri):
        for playlist in self.playlists:
            if playlist.uri == uri:
                tracks = self.backend.library.lookup(uri)
                return playlist.copy(tracks=tracks)

    def refresh(self):
        self.playlists = []
        self.backend.somafm_client.refresh()
        for channel in self.backend.somafm_client.channels():
            playlist = Playlist(uri='somafm://' +  channel, name=channel)
            self.playlists.append(playlist)

        backend.BackendListener.send('playlists_loaded')

    def save(self):
        pass
