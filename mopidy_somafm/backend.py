import logging

import mopidy_somafm
import pykka
from mopidy import backend
from mopidy.models import Album, Artist, Image, Ref, Track

from .somafm import SomaFMClient

logger = logging.getLogger(__name__)


class SomaFMBackend(pykka.ThreadingActor, backend.Backend):
    def __init__(self, config, audio):
        super().__init__()

        self.somafm = SomaFMClient(
            config["proxy"],
            "{}/{}".format(
                mopidy_somafm.Extension.dist_name, mopidy_somafm.__version__
            ),
        )
        self.library = SomaFMLibraryProvider(backend=self)

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
            uri="somafm:channel:/%s" % (channel_name),
        )

        track = Track(
            artists=[artist],
            album=album,
            last_modified=channel_data["updated"],
            comment=channel_data["description"],
            genre=channel_data["genre"],
            name=channel_data["title"],
            uri=channel_data["pls"],
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

        images = []

        for uri in uris:
            if uri.startswith("somafm:"):
                channel_name = uri[uri.index("/") + 1 :]

                image = Image(uri=self.backend.somafm.images[channel_name])
                images.append(image)

        return images
