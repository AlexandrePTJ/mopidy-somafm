import collections
import logging
import re
from urllib.parse import urlsplit

import requests

from mopidy import httpclient

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


class SomaFMClient:

    CHANNELS_URI = "https://api.somafm.com/channels.xml"

    # All channels seem to have this combination of quality/encoding available
    FALLBACK_QUALITY = "fast"
    FALLBACK_ENCODING = "mp3"

    channels = {}
    images = {}

    def __init__(self, proxy_config=None, user_agent=None):
        super().__init__()

        # Build requests session
        self.session = requests.Session()
        if proxy_config is not None:
            proxy = httpclient.format_proxy(proxy_config)
            self.session.proxies.update({"http": proxy, "https": proxy})

        full_user_agent = httpclient.format_user_agent(user_agent)
        self.session.headers.update({"user-agent": full_user_agent})

    def refresh(self, encoding, quality):
        # clean previous data
        self.channels = {}

        # download channels xml file
        channels_content = self._downloadContent(self.CHANNELS_URI)
        if channels_content is None:
            logger.error("Cannot fetch %s" % (self.CHANNELS_URI))
            return

        # parse XML
        root = ET.fromstring(channels_content)

        for child_channel in root:

            pls_id = child_channel.attrib["id"]
            channel_data = {}
            channel_all_pls = collections.defaultdict(dict)

            for child_detail in child_channel:

                key = child_detail.tag
                val = child_detail.text

                if key in ["title", "image", "dj", "genre", "description"]:
                    channel_data[key] = val
                elif key == "updated":
                    channel_data["updated"] = int(val)
                elif "pls" in key:
                    pls_quality = key[:-3]
                    pls_format = child_detail.attrib["format"]

                    channel_all_pls[pls_quality][pls_format] = val

                    # firewall playlist are fastpls+mp3 but with fw path
                    if pls_quality == "fast" and pls_format == "mp3":
                        r1 = urlsplit(val)
                        channel_all_pls["firewall"][
                            "mp3"
                        ] = "{}://{}/{}".format(
                            r1.scheme, r1.netloc, "fw" + r1.path
                        )

            channel_pls = self._choose_pls(channel_all_pls, encoding, quality)

            if channel_pls is not None:
                channel_data["pls"] = channel_pls
                self.channels[pls_id] = channel_data
                self.images[pls_id] = channel_data["image"]

        logger.info("Loaded %i SomaFM channels" % (len(self.channels)))

    def extractStreamUrlFromPls(self, pls_uri):
        pls_content = self._downloadContent(pls_uri)
        if pls_content is None:
            logger.error("Cannot fetch %s" % (pls_uri))
            return pls_uri

        # try to find FileX=<stream url>
        try:
            m = re.search(r"^(File\d)=(?P<stream_url>\S+)", pls_content, re.M)
            if m:
                return m.group("stream_url")
            else:
                return pls_uri
        except BaseException:
            return pls_uri

    def _choose_pls(self, all_pls, encoding, quality):
        if not all_pls:
            return None

        if quality in all_pls:
            quality_pls = all_pls[quality]
        elif self.FALLBACK_QUALITY in all_pls:
            quality_pls = all_pls[self.FALLBACK_QUALITY]
        else:
            quality_pls = all_pls[next(iter(all_pls))]

        if not quality_pls:
            return None

        if encoding in quality_pls:
            pls = quality_pls[encoding]
        elif self.FALLBACK_ENCODING in all_pls:
            pls = quality_pls[self.FALLBACK_ENCODING]
        else:
            pls = quality_pls[next(iter(quality_pls))]

        return pls

    def _downloadContent(self, url):
        try:
            r = self.session.get(url)
            logger.debug("Get %s : %i", url, r.status_code)

            if r.status_code != 200:
                logger.error(
                    "SomaFM: %s is not reachable [http code:%i]",
                    url,
                    r.status_code,
                )
                return None

        except requests.exceptions.RequestException as e:
            logger.error("SomaFM RequestException: %s", e)
        except requests.exceptions.ConnectionError as e:
            logger.error("SomaFM ConnectionError: %s", e)
        except requests.exceptions.URLRequired as e:
            logger.error("SomaFM URLRequired: %s", e)
        except requests.exceptions.TooManyRedirects as e:
            logger.error("SomaFM TooManyRedirects: %s", e)
        except Exception as e:
            logger.error("SomaFM exception: %s", e)
        else:
            return r.text

        return None
