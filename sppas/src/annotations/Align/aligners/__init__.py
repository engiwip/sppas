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

    annotations.Align.aligners.__init__.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

How to get the list of supported aligner names?

>>> a = sppasAligners()
>>> a.default_aligner_name()
>>> a.aligner_names()

How to get an instance of a given aligner?

>>> a1 = sppasAligners().instantiate(model_dir, "julius")
>>> a2 = JuliusAligner(model_dir)

"""
from .aligner import sppasAligners
from .basicalign import BasicAligner
from .juliusalign import JuliusAligner
from .hvitealign import HviteAligner

# ---------------------------------------------------------------------------

__all__ = (
    'sppasAligners',
    'JuliusAligner',
    'HviteAligner',
    'BasicAligner'
)

