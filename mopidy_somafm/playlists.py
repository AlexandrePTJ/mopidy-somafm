from __future__ import unicode_literals

from mopidy.backends import base, listener
from mopidy.models import Playlist

logger = logging.getLogger('mopidy.backends.somafm')


class SomaFMPlaylistsProvider(base.BasePlaylistsProvider):

    CHANNELS_URI = "http://api.somafm.com/channels.xml"

    def __init__(self, *args, **kwargs):
        super(SomaFMPlaylistsProvider, self).__init__(*args, **kwargs)
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
