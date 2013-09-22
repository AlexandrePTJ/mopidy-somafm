#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import ConfigParser
import datetime
import errno
import logging
import os
import os.path
import requests
import tempfile
import urlparse
from xml.dom import minidom

from mopidy.models import Track, Artist, Album, Playlist

logger = logging.getLogger('mopidy.backends.somafm.client')

'''
    Channels are playlist
    PLS are albums
    PLS contents are tracks
'''
class SomaFMClient(object):

    CHANNELS_URI = "http://api.somafm.com/channels.xml"

    def __init__(self):
        super(SomaFMClient, self).__init__()
        self.albums = []
        self.tracks = []
        self.playlists = []
        self.http_client = requests.Session()

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
        self.playlists[:] = []

        r = self.http_client.get(self.CHANNELS_URI)
        logger.debug("Get %s : %d", self.CHANNELS_URI, r.status_code)

        if r.status_code is not 200:
            logger.error("SomaFM: %s is not reachable", self.CHANNELS_URI)
            return

        self.parseChannelsXml(minidom.parseString(r.text))

    def parseChannelsXml(self, domDocument):
        for dmChannel in domDocument.getElementsByTagName("channel"):

            artist_kwargs = {}
            albums_kwargs = []
            playlist_kwargs = {}
            tracks_kwargs = {}
            images_uris = []

            if 'id' in dmChannel.attributes.keys():
                playlist_kwargs['uri'] = 'somafm:playlist:%s' % dmChannel.attributes['id'].nodeValue
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

            for childn in dmChannel.childNodes:
                if childn.nodeType == minidom.Node.ELEMENT_NODE:
                    key = childn.nodeName

                    # In case of empty element
                    if childn.firstChild is None:
                        continue

                    if key == 'title':
                        playlist_kwargs['name'] = childn.firstChild.nodeValue
                    elif 'image' in key:
                        images_uris.append(childn.firstChild.nodeValue)
                    elif key == 'dj':
                        artist_kwargs['name'] = childn.firstChild.nodeValue
                        artist_kwargs['uri'] = 'somafm:artist:%s' % childn.firstChild.nodeValue
                    elif 'pls' in key:
                        # extract pls file name without extension to create album name
                        plsURI = childn.firstChild.nodeValue
                        plsName = plsURI[plsURI.rfind('/') + 1:plsURI.rfind('.')]

                        # extract tracks infos
                        tracks_kwargs[plsName] = self.parsePls(childn.firstChild.nodeValue, channel_pls_path)

                        album_kws = {}
                        album_kws['name'] = plsName
                        album_kws['uri'] = 'somafm:album:%s' % plsName
                        albums_kwargs.append(album_kws)

            # when all nodes and pls are parsed, it buils all models and links
            artist = Artist(**artist_kwargs)

            album_dict = {}
            for album_kw in albums_kwargs:
                album_kw['artists'] = [artist]
                album_kw['images'] = images_uris
                album_kw['num_tracks'] = len(tracks_kwargs[album_kw['name']])

                # create Album and add to temp dict to assign into tracks
                album = Album(**album_kw)
                album_dict[album.name] = album
                self.albums.append(album)

            tracks_list = []
            for albumName in tracks_kwargs:
                for track_kw in tracks_kwargs[albumName]:
                    track_kw['album'] = album_dict[albumName]
                    track_kw['artists'] = [artist]

                    track = Track(**track_kw)
                    tracks_list.append(track)
                    self.tracks.append(track)

            playlist_kwargs['tracks'] = tracks_list
            playlist = Playlist(**playlist_kwargs)
            self.playlists.append(playlist)

    def parsePls(self, plsURI, plsLocalDirPath):

        # extract filename
        o = urlparse.urlparse(plsURI)
        plsFileName = o.path[o.path.rfind('/') + 1:]

        # download pls if needed
        download_pls = True
        if plsLocalDirPath is not None:
            download_pls = not os.path.exists(plsLocalDirPath + "/" + plsFileName)

        if download_pls:
            r = self.http_client.get(plsURI)
            logger.debug("Get %s : %d", plsURI, r.status_code)

            if r.status_code is not 200:
                logger.error("SomaFM: %s is not reachable", plsURI)
                return None

            # create temporary file or save to cache because ConfigParser need a file
            if plsLocalDirPath:
                with open(plsLocalDirPath + "/" + plsFileName, 'wb') as f:
                    for chunk in r.iter_content():
                        f.write(chunk)
                plsf = open(plsLocalDirPath + "/" + plsFileName, 'r')
            else:
                plsf = tempfile.NamedTemporaryFile()
                plsf.write(r.text)
                plsf.seek(0)

        else:
            plsf = open(plsLocalDirPath + "/" + plsFileName, 'r')

        # parse it
        parser = ConfigParser.RawConfigParser()
        try:
            parser.readfp(plsf)
        except ConfigParser.MissingSectionHeaderError:
            logger.error("SomaFM: %s is not a valid PLS file", plsURI)

        # close and delete temp file
        plsf.close()

        if not parser.has_section('playlist'):
            logger.error("SomaFM: %s has no section 'playlist'", plsURI)
            return None

        try:
            numberofentries = parser.getint('playlist', 'numberofentries')
        except (ConfigParser.NoOptionError, ValueError):
            logger.error("SomaFM: %s contains invalid data", plsURI)
            return None

        tracks_kwargs = []

        for idx in range(1, numberofentries + 1):
            track_kwargs = {}
            track_kwargs['track_no'] = idx - 1
            track_kwargs['uri'] = parser.get('playlist', 'file%d' % idx)
            track_kwargs['name'] = parser.get('playlist', 'title%d' % idx)
            track_kwargs['length'] = - 1
            tracks_kwargs.append(track_kwargs)

        return tracks_kwargs
