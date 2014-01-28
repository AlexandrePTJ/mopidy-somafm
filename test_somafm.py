#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import logging
from mopidy_somafm.somafm import SomaFMClient

logger = logging.getLogger("mopidy_somafm.somafm")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("--- %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

sfmc = SomaFMClient()
sfmc.refresh()

print sfmc.channels()
