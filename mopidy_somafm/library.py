from __future__ import unicode_literals

from mopidy.backends import base, listener
from mopidy.models import Playlist

logger = logging.getLogger('mopidy.backends.somafm')


class SomaFMLibraryProvider(base.BasePlaylistsProvider):

    def __init__(self, *args, **kwargs):
        super(SomaFMLibraryProvider, self).__init__(*args, **kwargs)
        self.refresh()

    def create(self, name):
        pass

    def delete(self, uri):
        pass

    def lookup(self, uri):
        pass

    def refresh(self):
        pass

    def save(self, playlist):
        pass
