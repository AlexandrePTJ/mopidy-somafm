from __future__ import unicode_literals

import logging
import pykka

from mopidy import backend
from mopidy.models import Playlist, Album, Track, Artist, Ref
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


'''
URI Scheme is :
    somafm:root => all playlists
    somafm:channel:/<channel name> => Playlist with misc pls path
    somafm:pls:/<channel name>/<pls name> => Track for browsing
    somafm:track:/<channel name>/<pls name> => Track for playing
'''


def parse_uri(uri):
    uri_split = uri.split(':', 3)
    if len(uri_split) >= 2 and uri_split[0] == 'somafm':
        sfmtype = uri_split[1]
        path = ''
        if len(uri_split) == 3:
            path = uri_split[2][1:]
        return sfmtype, path
    return None, None


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
        self.playlists = SomaFMPlaylistsProvider(backend=self)

        self.uri_schemes = ['somafm']

    def on_start(self):
        self.playlists.refresh()


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
        self.backend.somafm.refresh()
        for channel in self.backend.somafm.channels:
            playlist = Playlist(
                uri='somafm:channel:/' + channel,
                name=self.backend.somafm.channels[channel]['title'])
            playlists.append(playlist)

        self.playlists = playlists
        logger.info('Loaded %i SomaFM playlists' % (len(self.playlists)))
        backend.BackendListener.send('playlists_loaded')

    def save(self):
        pass


class SomaFMLibraryProvider(backend.LibraryProvider):

    root_directory = Ref.directory(uri='somafm:root', name='Soma FM')

    def lookup(self, uri):

        sfmtype, path = parse_uri(uri)
        if sfmtype is None:
            logger.debug('Unknown URI: %s' % (uri))
            return None
        if sfmtype not in ('channel', 'pls', 'track'):
            logger.debug('Unmanaged type: %s' % (sfmtype))
            return None

        channel_name = ''
        pls_name = ''
        if sfmtype == 'channel':
            channel_name = path
        else:
            path_split = path.split('/', 2)
            channel_name = path_split[0]
            pls_name = path_split[1]

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

        # PLS is a track
        if sfmtype == 'channel':
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
        elif sfmtype == 'pls':
            return [Track(
                artists=[artist],
                album=album,
                genre=channel_data['genre'],
                name=channel_data['pls'][pls_name]['name'],
                uri='somafm:track:/%s/%s' % (channel_name, pls_name)
                )]
        else:
            return [Track(
                artists=[artist],
                album=album,
                genre=channel_data['genre'],
                name=channel_data['pls'][pls_name]['name'],
                uri=channel_data['pls'][pls_name]['uri']
                )]

    def browse(self, uri):
        result = []

        sfmtype, path = parse_uri(uri)
        if sfmtype is None:
            logger.debug('Unknown URI: %s' % (uri))
            return result
        if sfmtype not in ('channel', 'root'):
            logger.debug('Unmanaged type: %s' % (sfmtype))
            return result

        if sfmtype == 'root':
            for channel in self.backend.somafm.channels:
                result.append(Ref.directory(
                    uri='somafm:channel:/%s' % (channel),
                    name=self.backend.somafm.channels[channel]['title']
                    ))

        elif sfmtype == 'channel':
            channel_data = self.backend.somafm.channels[path]
            for pls in channel_data['pls']:
                pls_data = channel_data['pls'][pls]
                result.append(Ref.track(
                    uri='somafm:pls:/%s/%s' % (path, pls),
                    name=pls_data['name']
                    ))

        result.sort(key=lambda ref: ref.name)
        return result
