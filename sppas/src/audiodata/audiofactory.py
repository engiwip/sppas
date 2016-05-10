#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# File: audiofactory.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------

from wave_io import WaveIO
from aiff_io import AiffIO
from sunau_io import SunauIO

# ----------------------------------------------------------------------------

class AudioFactory(object):
    """
    Factory for Audio.

    """

    __AUDIO = {
        "wav":  WaveIO,
        "wave": WaveIO,
        "aiff": AiffIO,
        "au" : SunauIO
        }

    @staticmethod
    def NewAudio(audio_type):
        """
        Return a new Audio according to the format.

        @param audio_type
        @return Audio

        """
        try:
            return AudioFactory.__AUDIO[audio_type]()
        except KeyError:
            raise Exception("Unrecognised Audio type: %s" % audio_type)

# ----------------------------------------------------------------------------