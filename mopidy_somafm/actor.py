from __future__ import unicode_literals

import logging
from mopidy import backend
from mopidy.models import Album, Artist, Ref, Track
import pykka
import mopidy_somafm
from .somafm import SomaFMClient


logger = logging.getLogger(__name__)


class SomaFMBackend(pykka.ThreadingActor, backend.Backend):

    def __init__(self, config, audio):
        super(SomaFMBackend, self).__init__()

        self.somafm = SomaFMClient(
            config['proxy'],
            "%s/%s" % (
                mopidy_somafm.Extension.dist_name,
                mopidy_somafm.__version__))
        self.library = SomaFMLibraryProvider(backend=self)

        self.uri_schemes = ['somafm']
        self.quality = config['somafm']['quality']
        self.encoding = config['somafm']['encoding']

    def on_start(self):
        self.somafm.refresh(self.encoding, self.quality)


class SomaFMLibraryProvider(backend.LibraryProvider):

    root_directory = Ref.directory(uri='somafm:root', name='Soma FM')

    def lookup(self, uri):
        # Whatever the uri, it will always contains one track
        # which is a url to a pls

        if not uri.startswith('somafm:'):
            return None

        channel_name = uri[uri.index('/') + 1:]
        channel_data = self.backend.somafm.channels[channel_name]

        # Artists
        artist = Artist(name=channel_data['dj'])

        # Build album (idem as playlist, but with more metada)
        album = Album(
            artists=[artist],
            date=channel_data['updated'],
            images=[channel_data['image']],
            name=channel_data['title'],
            uri='somafm:channel:/%s' % (channel_name))

        track = Track(
            artists=[artist],
            album=album,
            genre=channel_data['genre'],
            name=channel_data['title'],
            uri=channel_data['pls'])

        return [track]

    def browse(self, uri):

        if uri != 'somafm:root':
            return []

        result = []
        for channel in self.backend.somafm.channels:
            result.append(Ref.track(
                uri='somafm:channel:/%s' % (channel),
                name=self.backend.somafm.channels[channel]['title']
                ))

        result.sort(key=lambda ref: ref.name)
        return result
