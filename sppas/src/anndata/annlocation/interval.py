# -*- coding: UTF-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    src.anndata.annloc.interval.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Localization of an interval between two sppasPoint instances.

"""
import logging
from ..anndataexc import AnnDataTypeError
from ..anndataexc import AnnDataEqTypeError
from ..anndataexc import IntervalBoundsError

from .localization import sppasBaseLocalization
from .point import sppasPoint
from .duration import sppasDuration

# ---------------------------------------------------------------------------


class sppasInterval(sppasBaseLocalization):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Representation of a localization as an interval.

    An interval is identified by two sppasPoint objects:

        - one is representing the beginning of the interval;
        - the other is representing the end of the interval.

    """
    def __init__(self, begin, end):
        """ Create a new sppasInterval instance.

        :param begin: (sppasPoint)
        :param end: (sppasPoint)

        """
        sppasBaseLocalization.__init__(self)

        if isinstance(begin, sppasPoint) is False:
            AnnDataTypeError(begin, "sppasPoint")

        if isinstance(end, sppasPoint) is False:
            AnnDataTypeError(end, "sppasPoint")

        if sppasInterval.check_types(begin, end) is False:
            raise AnnDataEqTypeError(begin, end)

        if sppasInterval.check_interval_bounds(begin, end) is False:
            raise IntervalBoundsError(begin, end)

        if begin >= end:
            logging.info('[WARNING] begin >= end with ({!s:s}, {!s:s})'.format(begin, end))

        self.__begin = begin
        self.__end = end

    # -----------------------------------------------------------------------

    def set(self, other):
        """ Set self members from another sppasInterval instance.

        :param other: (sppasInterval)

        """
        if isinstance(other, sppasInterval) is False:
            raise AnnDataTypeError(other, "sppasInterval")

        self.__begin = other.get_begin()
        self.__end = other.get_end()

    # -----------------------------------------------------------------------

    def is_interval(self):
        """ Overrides. Return True, because self is representing an interval. """

        return True

    # -----------------------------------------------------------------------

    def copy(self):
        """ Return a deep copy of self. """

        return sppasInterval(self.__begin.copy(), self.__end.copy())

    # -----------------------------------------------------------------------

    def get_begin(self):
        """ Return the begin sppasPoint instance. """

        return self.__begin

    # -----------------------------------------------------------------------

    def set_begin(self, tp):
        """ Set the begin of the interval to a new sppasPoint.
        Attention: it is a reference assignment.

        :param tp: (sppasPoint)

        """
        if isinstance(tp, sppasPoint) is False:
            raise AnnDataTypeError(tp, "sppasPoint")

        if sppasInterval.check_types(tp, self.__end) is False:
            raise AnnDataEqTypeError(tp, self.__end)

        if sppasInterval.check_interval_bounds(tp, self.__end) is False:
            raise IntervalBoundsError(tp, self.__end)

        # assign the reference
        self.__begin = tp

    # -----------------------------------------------------------------------

    def get_end(self):
        """ Return the end sppasPoint instance. """

        return self.__end

    # -----------------------------------------------------------------------

    def set_end(self, tp):
        """ Set the end of the interval to a new sppasPoint.
        Attention: it is a reference assignment.

        :param tp: (sppasPoint)

        """
        if isinstance(tp, sppasPoint) is False:
            raise AnnDataTypeError(tp, "sppasPoint")

        if sppasInterval.check_types(self.__begin, tp) is False:
            raise AnnDataEqTypeError(self.__begin, tp)

        if sppasInterval.check_interval_bounds(self.__begin, tp) is False:
            raise IntervalBoundsError(self.__begin, tp)

        # assign the reference
        self.__end = tp

    # -----------------------------------------------------------------------

    def is_bound(self, point):
        """ Return True if point is the begin or the end of the interval. """

        return self.__begin == point or self.__end == point

    # -----------------------------------------------------------------------

    def combine(self, other):
        """ Return a sppasInterval, the combination of two intervals.

        :param other: (sppasInterval) the other interval to combine with.

        """
        if isinstance(other, sppasInterval) is False:
            AnnDataTypeError(other, "sppasInterval")

        if self > other:
            other, self = self, other

        if self.__end <= other.get_begin():
            return sppasInterval(self.__begin, other.get_end())

        return sppasInterval(other.get_begin(), self.__end)

    # -----------------------------------------------------------------------

    def union(self, other):
        """ Return a sppasInterval representing the union of two intervals.

        :param other: (sppasInterval) the other interval to merge with.

        """
        if isinstance(other, sppasInterval) is False:
            AnnDataTypeError(other, "sppasInterval")

        if self > other:
            other, self = self, other

        return sppasInterval(self.__begin, other.get_end())

    # -----------------------------------------------------------------------

    def duration(self):
        """ Overrides. Return the duration of the time interval.

        :returns: (sppasDuration) Duration and its vagueness.

        """
        # duration is the difference between the midpoints
        value = self.get_end().get_midpoint() - self.get_begin().get_midpoint()

        # vagueness of the duration is based on begin/end radius values
        vagueness = 0
        if self.get_begin().get_radius() is not None:
            vagueness += self.get_begin().get_radius()
        if self.get_end().get_radius() is not None:
            vagueness += self.get_end().get_radius()

        return sppasDuration(value, vagueness)

    # -----------------------------------------------------------------------

    @staticmethod
    def check_interval_bounds(begin, end):

        if begin.get_midpoint() >= end.get_midpoint():
            return False

        if begin.get_radius() is not None and end.get_radius() is not None:
            if begin.get_midpoint() - begin.get_radius() > end.get_midpoint() - end.get_radius():
                return False

        return True

    # -----------------------------------------------------------------------

    @staticmethod
    def check_types(begin, end):
        """ True only if begin and end are both the same types of sppasPoint().

        :param begin: any kind of data
        :param end: any kind of data
        :return: Boolean

        """
        try:
            begin.get_midpoint()
            end.get_midpoint()
        except AttributeError:
            return False

        return isinstance(begin.get_midpoint(), type(end.get_midpoint()))

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __repr__(self):
        return "sppasInterval: [{!s:s},{!s:s}]".format(self.get_begin(), self.get_end())

    def __str__(self):
        return "[{!s:s},{!s:s}]".format(self.get_begin(), self.get_end())

    # -----------------------------------------------------------------------

    def __contains__(self, other):
        """ Return True if the given data is contained in the interval.

        :param other: (sppasInterval, sppasPoint, int, float) the point to verify.

        """
        if isinstance(other, (sppasInterval, sppasPoint, float, int,)) is False:
            raise AnnDataTypeError(other, "sppasInterval, sppasPoint, float, int")

        if isinstance(other, sppasInterval):
            return (self.__begin <= other.get_begin() and
                    other.get_end() <= self.__end)

        return self.__begin <= other <= self.__end

    # -----------------------------------------------------------------------

    def __eq__(self, other):
        """ Equal.

        :param other: (sppasInterval) the other interval to compare with.

        """
        if isinstance(other, sppasInterval) is False:
            return False

        return (self.__begin == other.get_begin() and
                self.__end == other.get_end())

    # -----------------------------------------------------------------------

    def __lt__(self, other):
        """ LowerThan.

        :param other: (sppasInterval, sppasPoint, float, int) the other to compare with.

        """
        if isinstance(other, (sppasPoint, float, int)):
            return self.__end < other

        if isinstance(other, sppasInterval) is False:
            return False

        return self.__begin < other.get_begin()

    # -----------------------------------------------------------------------

    def __gt__(self, other):
        """ GreaterThan.

        :param other: (sppasInterval, sppasPoint, float, int) the other to compare with.

        """
        if isinstance(other, (int, float, sppasPoint)):
            return self.__begin > other

        if isinstance(other, sppasInterval) is False:
            return False

        return self.__begin > other.get_begin()
