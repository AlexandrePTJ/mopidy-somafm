from __future__ import unicode_literals

import logging

from mopidy import backend

logger = logging.getLogger(__name__)


class SomaFMLibraryProvider(backend.PlaylistsProvider):

    root_directory = None

    def lookup(self, uri):
        for playlist in self.backend.playlists.playlists:
            if playlist.uri == uri:
                return playlist.tracks
