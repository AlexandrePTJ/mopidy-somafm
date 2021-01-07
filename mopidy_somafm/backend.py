import logging

import mopidy_somafm
import pykka
import requests
import configparser
import random
from mopidy import backend, httpclient
from mopidy.models import Album, Artist, Image, Ref, Track

from .somafm import SomaFMClient

logger = logging.getLogger(__name__)


class SomaFMBackend(pykka.ThreadingActor, backend.Backend):
    def __init__(self, config, audio):
        super().__init__()

        user_agent = "{}/{}".format(
            mopidy_somafm.Extension.dist_name, mopidy_somafm.__version__
        )

        self.somafm = SomaFMClient(config["proxy"], user_agent)
        self.library = SomaFMLibraryProvider(backend=self)
        self.playback = SomaFMPlayback(
            audio=audio,
            backend=self,
            proxy_config=config["proxy"],
            user_agent=user_agent,
        )

        self.uri_schemes = ["somafm"]
        self.quality = config["somafm"]["quality"]
        self.encoding = config["somafm"]["encoding"]
        self.dj_as_artist = config["somafm"]["dj_as_artist"]

    def on_start(self):
        self.somafm.refresh(self.encoding, self.quality)


class SomaFMLibraryProvider(backend.LibraryProvider):

    root_directory = Ref.directory(uri="somafm:root", name="SomaFM")

    def lookup(self, uri):
        # Whatever the uri, it will always contains one track
        # which is a url to a pls

        if not uri.startswith("somafm:"):
            return None

        channel_name = uri[uri.index("/") + 1 :]
        channel_data = self.backend.somafm.channels[channel_name]

        # Artists
        if self.backend.dj_as_artist:
            artist = Artist(name=channel_data["dj"])
        else:
            artist = Artist()

        # Build album (idem as playlist, but with more metada)
        album = Album(
            artists=[artist],
            name=channel_data["title"],
        )

        track = Track(
            artists=[artist],
            album=album,
            last_modified=channel_data["updated"],
            comment=channel_data["description"],
            genre=channel_data["genre"],
            name=channel_data["title"],
            uri="somafm:channel:/%s" % (channel_name),
        )

        return [track]

    def browse(self, uri):

        if uri != "somafm:root":
            return []

        result = []
        for channel in self.backend.somafm.channels:
            result.append(
                Ref.track(
                    uri="somafm:channel:/%s" % (channel),
                    name=self.backend.somafm.channels[channel]["title"],
                )
            )

        result.sort(key=lambda ref: ref.name.lower())
        return result

    def get_images(self, uris):

        images = {}

        for uri in uris:
            if uri.startswith("somafm:"):
                channel_name = uri[uri.index("/") + 1 :]

                image = Image(uri=self.backend.somafm.images[channel_name])
                images[uri] = [image]

        return images


class SomaFMPlayback(backend.PlaybackProvider):
    def __init__(self, audio, backend, proxy_config=None, user_agent=None):
        super().__init__(audio=audio, backend=backend)

        # Build requests session
        self.session = requests.Session()
        if proxy_config is not None:
            proxy = httpclient.format_proxy(proxy_config)
            self.session.proxies.update({"http": proxy, "https": proxy})

        full_user_agent = httpclient.format_user_agent(user_agent)
        self.session.headers.update({"user-agent": full_user_agent})

    def translate_uri(self, uri):
        try:
            channel_name = uri[uri.index("/") + 1 :]
            channel_data = self.backend.somafm.channels.get(channel_name)

            r = self.session.get(channel_data["pls"])
            if r.status_code != 200:
                return None

            pls = configparser.ConfigParser()
            pls.read_string(r.text)
            playlist = pls["playlist"]
            num = int(playlist["numberofentries"])
            return playlist["File" + str(random.randint(1, num))]

        except Exception:
            return None
