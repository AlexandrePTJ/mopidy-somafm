#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime
import logging
import requests
import urlparse

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

'''
    Channels are playlist and Album
    PLS are tracks
    PLS contents for internal use
'''


class SomaFMClient(object):

    CHANNELS_URI = "http://api.somafm.com/channels.xml"
    channels = {}
    proxies = None

    def __init__(self, proxy=None):
        super(SomaFMClient, self).__init__()

        if proxy is not None:
            r1 = urlparse.urlsplit(proxy)
            self.proxies = {r1.scheme: proxy}

    def refresh(self):
        # clean previous data
        self.channels = {}

        # download channels xml file
        channels_content = self._downloadContent(self.CHANNELS_URI)
        if channels_content is None:
            logger.error('Cannot fetch %s' % (self.CHANNELS_URI))
            return

        # parse XML
        root = ET.fromstring(channels_content)

        for child_channel in root:

            pls_id = child_channel.attrib['id']

            self.channels[pls_id] = {}
            pls = {}

            for child_detail in child_channel:

                key = child_detail.tag
                val = child_detail.text

                if key in ['title', 'image', 'dj', 'genre']:
                    self.channels[pls_id][key] = val
                elif key == 'updated':
                    self.channels[pls_id]['updated'] = datetime.fromtimestamp(
                        int(val)).strftime("%Y-%m-%d")
                elif 'pls' in key:
                    pls[key] = {}
                    pls[key]['format'] = child_detail.attrib['format']
                    pls[key]['uri'] = val
                    # extract filename without extension to create album name
                    pls[key]['name'] = val[val.rfind('/') + 1:val.rfind('.')]

            self.channels[pls_id]['pls'] = pls

    def _downloadContent(self, url):
        try:
            r = requests.get(url, proxies=self.proxies)
            logger.debug("Get %s : %i", url, r.status_code)

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
