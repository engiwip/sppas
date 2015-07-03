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
#       Copyright (C) 2014-2015  Brigitte Bigi
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
# File: framepoint.py
# ----------------------------------------------------------------------------

import baseplacement
from ..utils.deprecated import deprecated

__docformat__ = """epytext"""
__authors__ = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


class FramePoint(baseplacement.BasePlacement):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, version 3
    @summary: This class is the FramePoint representation.

    Represents a frame point identified by a frame value and a radius value.
    This is used to reference a placement in a media, depending on its
    frame rate.

    In the FramePoint instance, the 3 relations <, = and > take into
    account a radius value, that represents the uncertainty of the placement.
    For a point x, with a radius value of dx, and a point y with a radius
    value of dy, these relations are defined as:
        - x = y iff |x - y| <= dx + dy
        - x < y iff not(x = y) and x < y
        - x > y iff not(x = y) and x > y

    Examples:

        - Strictly equals:

            - x = 3, dx=0.
            - y = 3, dy=0.
            - x = y is true

            - x = 3, dx=0.
            - y = 2, dy=0.
            - x = y is false

        - Using the radius:
            - x = 3, dx=1.
            - y = 2, dy=0.
            - x = y is true (due to a vagueness of 1 frame around x)

    """

    def __init__(self, frame, radius=0):
        """
        Create a new FramePoint instance.

        @param frame (int) rank of the frame in the media.
        @param radius (int) represents the vagueness of the point.

        @raise TypeError
        @raise ValueError

        """
        self.__frame = 0
        self.__radius = 0

        self.SetMidpoint(frame)
        self.SetRadius(radius)

    # End __init__
    # ------------------------------------------------------------------------------------

    def Set(self, other):
        """
        Set the frame/radius of another FramePoint instance.

        @param other (FramePoint)

        @raise TypeError

        """

        if isinstance(other, FramePoint) is False:
            raise TypeError("FramePoint argument required, not %r" % other)

        other = other.Copy()
        self.__frame = other.__frame
        self.__radius = other.__radius

    # End Set
    # ------------------------------------------------------------------------------------

    @deprecated
    def GetValue(self):
        """
        """
        self.GetMidpoint()

    # End GetValue
    # ------------------------------------------------------------------------------------

    def GetMidpoint(self):
        """
        Return the Frame value (int), i.e. the rank of the frame in the media.

        """
        return self.__frame

    # End GetMidpoint
    # ------------------------------------------------------------------------------------

    @deprecated
    def SetValue(self, frame):
        """
        @deprecated: replaced by SetMidpoint
        """
        self.SetMidpoint(frame)

    # End SetValue
    # ------------------------------------------------------------------------------------

    def SetMidpoint(self, frame):
        """
        Set this FramePoint to a new value.

        @param frame (int) is the new frame to set.

        @raise TypeError (if frame is not int)

        """
        if not isinstance(frame, int):
            raise TypeError("Integer argument required, not %r" % frame)

        if frame < 0:
            raise ValueError("A frame point can't be negative: %r" % frame)

        self.__frame = frame

    # End SetMidpoint
    # ------------------------------------------------------------------------------------

    def GetRadius(self):
        """
        Return the radius (int).

        """
        return self.__radius

    # End GetRadius
    # ------------------------------------------------------------------------------------

    def SetRadius(self, radius):
        """
        Fix the radius, in number of frames.

        @param radius (int) is the vagueness of the localization.

        @raise TypeError (if radius is not int)

        """
        if not isinstance(radius, int):
            raise TypeError("Integer argument required, not %r" % radius)

        if radius < 0.:
            raise ValueError(
                "The vagueness of a frame point can't be negative: %r"
                % radius)

        if self.__frame < radius:
            radius = self.__frame

        self.__radius = radius

    # End SetRadius
    # ------------------------------------------------------------------------------------

    def IsPoint(self):
        """
        Return True, as this object is representing a Point.

        """
        return True

    # End IsPoint
    # ------------------------------------------------------------------------------------

    def IsFramePoint(self):
        """
        Return True, as this object is an instance of FramePoint.

        """
        return True

    # End IsFramePoint
    # ------------------------------------------------------------------------------------

    def Duration(self):
        """
        Return the duration of the frame point, in number of frames.
        Represents the duration of the vagueness.

        """

        return 2*self.__radius

    # End Duration
    # ------------------------------------------------------------------------------------

    def Copy(self):
        """
        Return a deep copy of self.

        """
        t = self.__frame
        r = self.__radius
        return FramePoint(t, r)

    # End Copy
    # ------------------------------------------------------------------------------------

    def __repr__(self):
        return "FramePoint: (%d,%d)" % (self.__frame, self.__radius)

    # End __repr__
    # ------------------------------------------------------------------------------------

    def __str__(self):
        return "(%d,%d)" % (self.__frame, self.__radius)

    # End __str__
    # ------------------------------------------------------------------------------------

    def __hash__(self):
        return hash((self.__frame, self.__radius))

    # End __hash__
    # ------------------------------------------------------------------------------------

    def __eq__(self, other):
        """
        Equal.
        This relationship takes into account the radius.

        @param other (FramePoint, int) is the other point to compare with.

        """
        if isinstance(other, (int, FramePoint)) is False:
            return False

        if isinstance(other, FramePoint) is True:
            delta = abs(self.__frame - other.GetMidpoint())
            radius = self.__radius + other.GetRadius()
            return delta <= radius

        if isinstance(other, (int, float)):
            delta = abs(self.__frame - other)
            radius = self.__radius
            return delta <= radius

    # End __eq__
    # ------------------------------------------------------------------------------------

    def __lt__(self, other):
        """
        LowerThan.
        This relationship takes into account the radius.

        @param other (FramePoint, int)
        is the other frame point to compare with.

        """
        if isinstance(other, FramePoint) is True:
            return self != other and self.__frame < other.GetMidpoint()

        return self != other and self.__frame < other

    # End __lt__
    # ------------------------------------------------------------------------------------

    def __gt__(self, other):
        """
        GreaterThan.
        This relationship takes into account the radius.

        @param other (FramePoint, int)
        is the other frame point to compare with.

        """
        if isinstance(other, FramePoint) is True:
            return self != other and self.__frame > other.GetMidpoint()

        return self != other and self.__frame > other

    # End __gt__
    # ------------------------------------------------------------------------------------

# End FramePoint
# ------------------------------------------------------------------------------------
