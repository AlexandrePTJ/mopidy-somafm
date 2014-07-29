#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime
import logging
import requests
import urlparse
import re

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

#
#  Channels are playlist and Album
#  PLS are tracks
#  PLS contents for internal use
#


class SomaFMClient(object):

    CHANNELS_URI = "http://api.somafm.com/channels.xml"
    channels = {}
    proxies = None

    def __init__(self, proxy=None):
        super(SomaFMClient, self).__init__()

        if proxy is not None:
            r1 = urlparse.urlsplit(proxy)
            self.proxies = {r1.scheme: proxy}

    def refresh(self, encoding, quality):
        # clean previous data
        self.channels = {}

        # adjust quality real name
        plsquality = quality
        if plsquality != 'firewall':
            plsquality += 'pls'

        # download channels xml file
        channels_content = self._downloadContent(self.CHANNELS_URI)
        if channels_content is None:
            logger.error('Cannot fetch %s' % (self.CHANNELS_URI))
            return

        # parse XML
        root = ET.fromstring(channels_content)

        for child_channel in root:

            pls_id = child_channel.attrib['id']
            channel_data = {}

            for child_detail in child_channel:

                key = child_detail.tag
                val = child_detail.text

                if key in ['title', 'image', 'dj', 'genre']:
                    channel_data[key] = val
                elif key == 'updated':
                    channel_data['updated'] = datetime.fromtimestamp(
                        int(val)).strftime("%Y-%m-%d")
                elif 'pls' in key:
                    plsformat = child_detail.attrib['format']

                    if (key == plsquality and plsformat == encoding):
                        channel_data['pls'] = val
                    # firewall playlist are fastpls+mp3 but with fw path
                    elif (
                            plsquality == 'firewall' and
                            key == 'fastpls' and plsformat == 'mp3'):
                        r1 = urlparse.urlsplit(val)
                        channel_data['pls'] = "%s://%s/%s" % (
                            r1.scheme, r1.netloc, 'fw' + r1.path)

            if 'pls' in channel_data:
                self.channels[pls_id] = channel_data

        logger.info('Loaded %i SomaFM channels' % (len(self.channels)))

    def extractStreamUrlFromPls(self, pls_uri):
        pls_content = self._downloadContent(pls_uri)
        if pls_content is None:
            logger.error('Cannot fetch %s' % (pls_uri))
            return pls_uri

        # try to find FileX=<stream url>
        try:
            m = re.search(
                r"^(File\d)=(?P<stream_url>\S+)",
                pls_content, re.M)
            if m:
                return m.group("stream_url")
            else:
                return pls_uri
        except:
            return pls_uri

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
