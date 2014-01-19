from __future__ import unicode_literals

import logging

from mopidy import backend
from mopidy.models import Playlist

logger = logging.getLogger(__name__)

class SomaFMPlaybackProvider(backend.PlaybackProvider):

    def play(self, track):
        logger.info(track)
        urls = self.backend.somafm_client.getSomaStreamURL(track.uri.split(':')[2])

        if urls is None:
            return False
        if len(urls) == 0:
            return False

        # Go through urls until one is started
        for url in urls:
            self.audio.prepare_change()
            self.audio.set_uri(url)
            if not self.audio.start_playback():
                logger.error('SomaFM audio: %s is invalid' % url)
            else:
                logger.debug('SomaFM audio: playing %s' % url)
                return True

        logger.error('SomaFM: No valid urls available for track %s' % track.uri)
        return False
