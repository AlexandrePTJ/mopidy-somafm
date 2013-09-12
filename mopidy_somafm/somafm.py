#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from xml.dom import minidom

import logging
import requests
import time

from requests.exceptions import RequestException
from mopidy.models import Track, Artist, Album
from urllib import quote_plus

logger = logging.getLogger('mopidy.backends.somafm.client')

'''
	Channels are albums
	PLS contents are tracks
'''

class SomaFMClient(object):

    #CHANNELS_URI = "http://api.somafm.com/channels.xml"
    CHANNELS_URI = "mopidy_somafm/channels.xml"

    def __init__(self):
    	super(SomaFMClient, self).__init__()
    	self.albums = []
    	self.tracks = []

    def refresh(self):
        #r = requests.get(self.CHANNELS_URI)
        #self.parseChannelsXml(minidom.parseString(r.text))
        self.parseChannelsXml(minidom.parse(self.CHANNELS_URI))

    def parseChannelsXml(self, domDocument):
    	for dmChannel in domDocument.getElementsByTagName("channel"):
    		print "-------------------------------------------------------"
    		album_kwargs = {}
    		album_kwargs['images'] = []
    		for childn in dmChannel.childNodes:
    			if childn.nodeType == minidom.Node.ELEMENT_NODE:
    				key = childn.nodeName
    				if key == 'title' and childn.firstChild is not None:
    					album_kwargs['name'] = childn.firstChild.nodeValue
    				elif 'image' in key and childn.firstChild is not None:
    					album_kwargs['images'].append(childn.firstChild.nodeValue)
    				elif key == 'dj' and childn.firstChild is not None:
    					artist_kwargs = {}
    					artist_kwargs['name'] = childn.firstChild.nodeValue
    					artist = Artist(**artist_kwargs)
    					album_kwargs['artists'] = [artist]
    				elif 'pls' in key:
    					pass

    		album = Album(**album_kwargs)
    		print album

    def parsePls(self, plsDocument):
    	pass

sfc = SomaFMClient()
sfc.refresh()
