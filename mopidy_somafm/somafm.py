#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from xml.dom import minidom

import logging
import requests
import ConfigParser
import datetime
import tempfile

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

            if dmChannel.attributes.has_key('id'):
                playlist_kwargs['uri'] = 'somafm:playlist:%s' % dmChannel.attributes['id'].nodeValue
            else:
                continue

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
                    elif key == 'updated':
                        pass
                        # TODO: something to fix here
                        #playlist_kwargs['last_modified'] = datetime.datetime.fromtimestamp(int(childn.firstChild.nodeValue))
                    elif 'pls' in key:
                        # extract pls file name without extension to create album name
                        plsURI = childn.firstChild.nodeValue
                        plsName = plsURI[plsURI.rfind('/') + 1:plsURI.rfind('.')]

                        # extract tracks infos
                        tracks_kwargs[plsName] = self.parsePls(childn.firstChild.nodeValue)

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

    def parsePls(self, plsURI):
        # download pls
        r = self.http_client.get(plsURI)
        logger.debug("Get %s : %d", plsURI, r.status_code)

        if r.status_code is not 200:
            logger.error("SomaFM: %s is not reachable", plsURI)
            return None

        # create temporary file because ConfigParser need a file
        plsf = tempfile.NamedTemporaryFile()
        plsf.write(r.text)
        plsf.seek(0)

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

# sfc = SomaFMClient()
# sfc.refresh()
# print sfc.playlists
