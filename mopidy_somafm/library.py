from __future__ import unicode_literals

import logging

from mopidy.backends import base, listener
from mopidy.models import Playlist

logger = logging.getLogger('mopidy.backends.somafm')


class SomaFMLibraryProvider(base.BasePlaylistsProvider):

    def __init__(self, *args, **kwargs):
        super(SomaFMLibraryProvider, self).__init__(*args, **kwargs)

    def find_exact(self, query, uris):
        pass

    def lookup(self, uri):
        for playlist in self.backend.somafm_client.playlists:
            if playlist.uri == uri:
                return playlist.tracks
        return None

    def refresh(self):
        pass

    def search(self, query, uris):
        pass
