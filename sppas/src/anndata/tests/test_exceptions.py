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

    src.anndata.tests.test_exceptions
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Test the anndata exceptions.

    to be continued... not all exceptions are tested!

"""
import unittest
from ..anndataexc import *

# -----------------------------------------------------------------------


class TestExceptions(unittest.TestCase):

    def test_exc_global(self):
        try:
            raise AnnDataError()
        except Exception as e:
            self.assertTrue(isinstance(e, AnnDataError))
            self.assertTrue(ANN_DATA_ERROR in str(e))

        try:
            raise AnnDataTypeError("observed_type", "expected_type")
        except Exception as e:
            self.assertTrue(isinstance(e, AnnDataTypeError))
            self.assertTrue(ANN_DATA_TYPE_ERROR in str(e))

        try:
            raise AnnDataIndexError(4)
        except Exception as e:
            self.assertTrue(isinstance(e, AnnDataIndexError))
            self.assertTrue(ANN_DATA_INDEX_ERROR in str(e))

        try:
            raise AnnDataEqTypeError("object", "object_ref")
        except Exception as e:
            self.assertTrue(isinstance(e, AnnDataEqTypeError))
            self.assertTrue(ANN_DATA_EQ_TYPE_ERROR in str(e))

        try:
            raise AnnDataNegValueError(-5)
        except Exception as e:
            self.assertTrue(isinstance(e, AnnDataNegValueError))
            self.assertTrue(ANN_DATA_NEG_VALUE_ERROR in str(e))

    def test_exc_Tier(self):
        try:
            raise TierAppendError(3, 5)
        except Exception as e:
            self.assertTrue(isinstance(e, TierAppendError))
            self.assertTrue(TIER_APPEND_ERROR in str(e))

        try:
            raise TierAddError(3)
        except Exception as e:
            self.assertTrue(isinstance(e, TierAddError))
            self.assertTrue(TIER_ADD_ERROR in str(e))

        try:
            raise TierHierarchyError("name")
        except Exception as e:
            self.assertTrue(isinstance(e, TierHierarchyError))
            self.assertTrue(TIER_HIERARCHY_ERROR in str(e))

        try:
            raise CtrlVocabContainsError("tag")
        except Exception as e:
            self.assertTrue(isinstance(e, CtrlVocabContainsError))
            self.assertTrue(CTRL_VOCAB_CONTAINS_ERROR in str(e))

        try:
            raise IntervalBoundsError("begin", "end")
        except Exception as e:
            self.assertTrue(isinstance(e, IntervalBoundsError))
            self.assertTrue(INTERVAL_BOUNDS_ERROR in str(e))

    def test_exc_Trs(self):
        try:
            raise TrsAddError("tier_name", "transcription_name")
        except Exception as e:
            self.assertTrue(isinstance(e, TrsAddError))
            self.assertTrue(TRS_ADD_ERROR in str(e))

        try:
            raise TrsRemoveError("tier_name", "transcription_name")
        except Exception as e:
            self.assertTrue(isinstance(e, TrsRemoveError))
            self.assertTrue(TRS_REMOVE_ERROR in str(e))

    def test_exc_AIO(self):
        try:
            raise AioEncodingError("filename", "error éèàçù")
        except Exception as e:
            self.assertTrue(isinstance(e, AioEncodingError))
            self.assertTrue(AIO_ENCODING_ERROR in str(e))

        try:
            raise AioFileExtensionError("filename")
        except Exception as e:
            self.assertTrue(isinstance(e, AioFileExtensionError))
            self.assertTrue(AIO_FILE_EXTENSION_ERROR in str(e))

        try:
            raise AioMultiTiersError("file_format")
        except Exception as e:
            self.assertTrue(isinstance(e, AioMultiTiersError))
            self.assertTrue(AIO_MULTI_TIERS_ERROR in str(e))

        try:
            raise AioNoTiersError("file_format")
        except Exception as e:
            self.assertTrue(isinstance(e, AioNoTiersError))
            self.assertTrue(AIO_NO_TIERS_ERROR in str(e))

        try:
            raise AioLineFormatError(3, "line")
        except Exception as e:
            self.assertTrue(isinstance(e, AioLineFormatError))
            self.assertTrue(AIO_LINE_FORMAT_ERROR in str(e))

        try:
            raise AioEmptyTierError("file_format", "tier_name")
        except Exception as e:
            self.assertTrue(isinstance(e, AioEmptyTierError))
            self.assertTrue(AIO_EMPTY_TIER_ERROR in str(e))
