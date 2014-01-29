from __future__ import unicode_literals

import logging
import pykka

from mopidy import backend
from mopidy.models import Playlist, Album, Track, Artist
from .somafm import SomaFMClient

logger = logging.getLogger(__name__)


def format_proxy(scheme, username, password, hostname, port):
    # Format Proxy URL
    if hostname:
        # scheme must exists, so if None is give, we set default to http
        if not scheme:
            scheme = "http"
        # idem with port, default at 80
        if not port:
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

        self.somafm_client = SomaFMClient(proxy=full_proxy)
        self.library = SomaFMLibraryProvider(backend=self)
        self.playlists = SomaFMPlaylistsProvider(backend=self)

        self.uri_schemes = ['somafm']

    def on_start(self):
        self.playlists.refresh()

    def on_stop(self):
        pass


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
        playlists = []
        self.backend.somafm_client.refresh()
        for channel in self.backend.somafm_client.channels:
            playlist = Playlist(
                uri='somafm://' + channel,
                name=self.backend.somafm_client.channels[channel]['title'])
            playlists.append(playlist)

        self.playlists = playlists
        logger.info('Loaded %i SomaFM playlists' % (len(self.playlists)))
        backend.BackendListener.send('playlists_loaded')

    def save(self):
        pass


class SomaFMLibraryProvider(backend.PlaylistsProvider):

    root_directory = None

    def search(self, query=None, uris=None):
        pass

    def lookup(self, uri):
        for playlist in self.backend.playlists.playlists:
            if playlist.uri == uri:
                channel_name = uri.replace('somafm://', '')
                channel_data = self.backend.somafm_client.channels[channel_name]

                ''' Artists '''
                artist = Artist(name=channel_data['dj'])

                ''' Build album (idem as playlist, but with more metada) '''
                album = Album(
                    artists=[artist],
                    date=channel_data['updated'],
                    images=[channel_data['image']],
                    name=channel_data['title'],
                    uri=uri)

                ''' PLS is a track '''
                tracks = []
                for pls in channel_data['pls']:
                    track = Track(
                        artists=[artist],
                        album=album,
                        genre=channel_data['genre'],
                        name=channel_data['pls'][pls]['name'],
                        uri=channel_data['pls'][pls]['uri']
                        )
                    tracks.append(track)
                return tracks
        return None
