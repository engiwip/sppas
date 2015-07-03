#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /        Automatic
#           \__   |__/  |__/  |___| \__      Annotation
#              \  |     |     |   |    \     of
#           ___/  |     |     |   | ___/     Speech
#           =============================
#
#           http://sldr.org/sldr000800/preview/
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2011-2015  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
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
# File: rutils.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import codecs
import pickle
import logging
import os
import os.path


# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

DUMP_FILENAME_EXT = ".dump"
ENCODING          = 'utf-8'
UNKNOWN_SYMBOL    = u"UNK"

# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------

def ToLower( entry ):
    """
    Return a unicode string with lower case.

    @entry (String or Unicode)
    @return Unicode

    """
    try:
        e = entry.decode('utf8')
    except Exception:
        e = entry
    e = e.lower()

    return e

# ----------------------------------------------------------------------------


def ToStrip( entry ):
    """
    To strip a string.
    (remove also multiple spaces inside the string)

    @entry (String or Unicode)
    @return Unicode

    """
    try:
        e = entry.decode('utf8')
    except Exception:
        e = entry
    e = e.replace(u'\ufeff', ' ')

    return ' '.join( e.split() )

# ----------------------------------------------------------------------------



def get_dump_filename(filename):
    """
    Return the file name of the dumped version of filename.

    @param filename (String)
    @return filename

    """

    fileName, fileExt = os.path.splitext(filename)

    return fileName + DUMP_FILENAME_EXT

# End get_dump_filename
# ----------------------------------------------------------------------------


def has_dump(filename):
    """
    Test if a dumped file exists for filename.

    @param filename (String)
    @return Boolean

    """
    dumpfilename = get_dump_filename(filename)
    if os.path.isfile( dumpfilename ):
        tascii = os.path.getmtime(filename)
        tdump  = os.path.getmtime(dumpfilename)
        if tascii < tdump:
            return True

    return False

# ----------------------------------------------------------------------------


def load_from_dump(filename):
    """
    Load the file from a dumped file.

    @param filename
    @return loaded data

    """
    if has_dump(filename) is False:
        return None

    dumpfilename = get_dump_filename(filename)

    try:
        with codecs.open(dumpfilename, 'rb') as f:
            data = pickle.load(f)
    except Exception as e:
        logging.info('Load dumped data failed: %s'%str(e))
        os.remove( dumpfilename )
        return None

    return data

# End load_from_dump
# ----------------------------------------------------------------------------


def save_as_dump(data, filename):
    """
    Save the data as a dumped file.

    @param data to save
    @param filename

    """
    dumpfilename = get_dump_filename(filename)

    try:
        with codecs.open(dumpfilename, 'wb') as f:
            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        logging.info('Save a dumped data failed: %s'%str(e))
        return False

    return True

# End save_as_dump
# ----------------------------------------------------------------------------
