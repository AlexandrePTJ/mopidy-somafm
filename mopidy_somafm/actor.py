from __future__ import unicode_literals

import logging
import pykka

from mopidy import backend
from mopidy.models import Album, Track, Artist, Ref
from .somafm import SomaFMClient

logger = logging.getLogger(__name__)


def format_proxy(scheme, username, password, hostname, port):
    # Format Proxy URL
    if hostname:
        # scheme must exists, so if None is give, we set default to http
        if not scheme:
            scheme = "http"
        # idem with port, default at 80
        if not port or port < 0:
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

        self.somafm = SomaFMClient(proxy=full_proxy)
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
