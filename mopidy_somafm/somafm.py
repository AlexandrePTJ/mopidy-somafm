#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import ConfigParser
import datetime
import errno
import io
import logging
import os
import os.path
import requests
import tempfile
import urlparse
from xml.dom import minidom

from mopidy import backend
from mopidy.models import Track, Artist, Album, Playlist

logger = logging.getLogger(__name__)

'''
    Channels are playlist and Album
    PLS are tracks
    PLS contents for internal use
'''


class SomaFMClient(object):

    CHANNELS_URI = "http://api.somafm.com/channels.xml"

    def __init__(self, backend, proxy):
        super(SomaFMClient, self).__init__()
        self.albums = []
        self.tracks = []
        self.artists = []
        self.playlists = []

        self.tracks_uris = {}
        self.backend = backend

        self.proxies = None
        if proxy is not None:
            r1 = urlparse.urlsplit(proxy)
            self.proxies = {r1.scheme: proxy}

        # try to create cache directory to keep pls files
        # if it fails, self.cache_dir will be set to 'None'
        try:
            self.cache_dir = tempfile.gettempdir() + "/mopidy_somafm"
            os.mkdir(self.cache_dir)
        except OSError, e:
            if e.errno is not errno.EEXIST:
                self.cache_dir = None

    def refresh(self):
        # clean previous data
        self.albums[:] = []
        self.tracks[:] = []
        self.artists[:] = []
        self.playlists[:] = []

        channels_content = self._downloadContent(self.CHANNELS_URI)
        if channels_content is None:
            return

        self._parseChannelsXml(minidom.parseString(channels_content))

        # We are done
        self.backend.playlists.playlists = self.playlists
        logger.info(
            'Loaded %s SomaFM playlist(s)',
            len(self.backend.playlists.playlists))
        backend.BackendListener.send('playlists_loaded')

    def getSomaStreamURL(self, track_key):
        if track_key in self.tracks_uris:
            return self.tracks_uris[track_key]
        else:
            return None

    def _downloadContent(self, url):
        try:
            r = requests.get(url, proxies=self.proxies)
            logger.debug("SomaFM: Get %s : %i", url, r.status_code)

            if r.status_code is not 200:
                logger.error(
                    "SomaFM: %s is not reachable [http code:%i]",
                    url, r.status_code)
                return None

        except requests.exceptions.RequestException, e:
            logger.error("SomaFM RequestException: %s", e)
        except requests.exceptions.ConnectionError, e:
            logger.error("SomaFM ConnectionError: %s", e)
        except requests.exceptions.URLRequired, e:
            logger.error("SomaFM URLRequired: %s", e)
        except requests.exceptions.TooManyRedirects, e:
            logger.error("SomaFM TooManyRedirects: %s", e)
        except Exception, e:
            logger.error("SomaFM exception: %s", e)
        else:
            return r.text

        return None

    def _parseChannelsXml(self, domDocument):
        for dmChannel in domDocument.getElementsByTagName("channel"):

            playlist_name = None
            playlist_title = None
            if 'id' in dmChannel.attributes.keys():
                playlist_name = dmChannel.attributes['id'].nodeValue
            else:
                continue

            # We need to have 'updated' value to be able to cache things
            # but only if cache_dir is not 'None'
            channel_updated = None
            channel_pls_path = None
            if self.cache_dir is not None:
                for childn in dmChannel.childNodes:
                    if childn.nodeType == minidom.Node.ELEMENT_NODE:
                        if childn.nodeName == 'updated':
                            channel_updated = childn.firstChild.nodeValue

                if channel_updated is None:
                    continue

                # create temp directory to keep pls files
                try:
                    channel_pls_path = self.cache_dir + "/" + channel_updated
                    os.mkdir(channel_pls_path)
                except OSError, e:
                    if e.errno is not errno.EEXIST:
                        channel_pls_path = None

            pls_content = {}
            images_uris = []
            dj_name = None
            for childn in dmChannel.childNodes:
                if childn.nodeType == minidom.Node.ELEMENT_NODE:
                    key = childn.nodeName

                    # In case of empty element
                    if childn.firstChild is None:
                        continue

                    if key == 'title':
                        playlist_title = childn.firstChild.nodeValue
                    elif 'image' in key:
                        images_uris.append(childn.firstChild.nodeValue)
                    elif key == 'dj':
                        dj_name = childn.firstChild.nodeValue
                    elif 'pls' in key:
                        # extract pls file name without extension to create
                        # album name
                        plsURI = childn.firstChild.nodeValue
                        plsName = plsURI[
                            plsURI.rfind('/') + 1:plsURI.rfind('.')]

                        # extract tracks infos
                        pls_tracks_uris = self._parsePls(
                            childn.firstChild.nodeValue, channel_pls_path)
                        if pls_tracks_uris is not None:
                            pls_content[plsName] = pls_tracks_uris

            # if nothing extracted, don't continue
            if len(pls_content) is 0:
                continue

            # Transform channel_updated to mopidy date string format
            # (YYYY-MM-DD)
            mopidy_date = datetime.datetime.fromtimestamp(
                int(channel_updated)).strftime("%Y-%m-%d")

            # when all nodes and pls are parsed, it buils all models and links
            artist_kwargs = {}
            artist_kwargs['name'] = dj_name
            artist = Artist(**artist_kwargs)
            pls_artists = [artist]
            self.artists.append(artist)

            album_kwargs = {}
            album_kwargs['uri'] = "somafm:album:%s" % playlist_name
            album_kwargs['name'] = playlist_title
            album_kwargs['artists'] = pls_artists
            album_kwargs['num_tracks'] = len(pls_content)
            album_kwargs['num_discs'] = 1
            album_kwargs['date'] = mopidy_date
            album_kwargs['images'] = images_uris
            album = Album(**album_kwargs)
            self.albums.append(album)

            pls_tracks = []
            track_no = 1
            for pslkey in pls_content:
                track_kwargs = {}
                track_kwargs['uri'] = "somafm:track:%s" % pslkey
                track_kwargs['name'] = pslkey
                track_kwargs['artists'] = pls_artists
                track_kwargs['album'] = album
                track_kwargs['track_no'] = track_no
                track_no = track_no + 1
                track_kwargs['date'] = mopidy_date

                track = Track(**track_kwargs)
                pls_tracks.append(track)
                self.tracks.append(track)

                self.tracks_uris[pslkey] = pls_content[pslkey]

            playlist_kwargs = {}
            playlist_kwargs['uri'] = "somafm:playlist:%s" % playlist_name
            playlist_kwargs['name'] = playlist_title
            playlist_kwargs['last_modified'] = mopidy_date
            playlist_kwargs['tracks'] = pls_tracks
            playlist = Playlist(**playlist_kwargs)
            self.playlists.append(playlist)

    def _getPlsContent(self, plsURI, plsLocalDirPath):
        # extract filename
        o = urlparse.urlparse(plsURI)
        plsFileName = o.path[o.path.rfind('/') + 1:]

        # download pls if needed
        download_pls = True
        if plsLocalDirPath is not None:
            download_pls = not os.path.exists(
                plsLocalDirPath + "/" + plsFileName)

        if download_pls:
            plsc = self._downloadContent(plsURI)

            if plsc is None:
                return None

            # save to local cache
            if plsLocalDirPath:
                with open(plsLocalDirPath + "/" + plsFileName, 'wb') as f:
                    f.write(plsc)
                f.close()

            return plsc
        else:
            with open(plsLocalDirPath + "/" + plsFileName, 'wb') as f:
                plsc = f.read()
            f.close()
            return plsc

    def _parsePls(self, plsURI, plsLocalDirPath):

        plsc = self._getPlsContent(plsURI, plsLocalDirPath)
        if plsc is None:
            return None

        # parse it
        parser = ConfigParser.RawConfigParser()
        try:
            parser.readfp(io.BytesIO(plsc))
        except ConfigParser.MissingSectionHeaderError:
            logger.error("SomaFM: %s is not a valid PLS file", plsURI)

        if not parser.has_section('playlist'):
            logger.error("SomaFM: %s has no section 'playlist'", plsURI)
            return None

        try:
            numberofentries = parser.getint('playlist', 'numberofentries')
        except (ConfigParser.NoOptionError, ValueError):
            logger.error("SomaFM: %s contains invalid data", plsURI)
            return None

        tracks_uris = []
        for idx in range(1, numberofentries + 1):
            tracks_uris.append(parser.get('playlist', 'file%d' % idx))

        return tracks_uris
