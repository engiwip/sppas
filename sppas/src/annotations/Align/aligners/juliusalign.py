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

    src.annotations.Align.aligners.juliusalign.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

http://julius.sourceforge.jp/en_index.php

`Julius` is a high-performance, two-pass large vocabulary continuous
speech recognition (LVCSR) decoder software for speech-related researchers
and developers. Based on word N-gram and context-dependent HMM, it can
perform almost real-time decoding on most current PCs in 60k word dictation
task. Major search techniques are fully incorporated such as tree lexicon,
N-gram factoring, cross-word context dependency handling, enveloped beam
search, Gaussian pruning, Gaussian selection, etc.
Besides search efficiency, it is also modularized carefully to be independent
from model structures, and various HMM types are supported such as
shared-state triphones and tied-mixture models, with any number of mixtures,
states, or phones. Standard formats are adopted to cope with other free
modeling toolkit such as HTK, CMU-Cam SLM toolkit, etc.

The main platform is Linux and other Unix workstations, and also works on
Windows. Most recent version is developed on Linux and Windows (cygwin /
mingw), and also has Microsoft SAPI version. Julius is distributed with
open license together with source codes.

Julius has been developed as a research software for Japanese LVCSR since
1997, and the work was continued under IPA Japanese dictation toolkit
project (1997-2000), Continuous Speech Recognition Consortium, Japan (CSRC)
(2000-2003) and currently Interactive Speech Technology Consortium (ISTC).

"""
import os
import codecs
from subprocess import Popen, PIPE, STDOUT

from sppas.src.config import sg
from sppas.src.config import symbols
from sppas.src.models.slm.ngramsmodel import sppasNgramsModel
from sppas.src.models.slm.arpaio import sppasArpaIO
from sppas.src.models.slm.ngramsmodel import START_SENT_SYMBOL, END_SENT_SYMBOL
from sppas.src.utils.makeunicode import sppasUnicode
from sppas.src.resources.dictpron import sppasDictPron

from .basealigner import BaseAligner

# ----------------------------------------------------------------------------

SIL_PHON = list(symbols.phone.keys())[list(symbols.phone.values()).index("silence")]

# ----------------------------------------------------------------------------


class JuliusAligner(BaseAligner):
    """Julius automatic alignment system.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    JuliusAligner is able to align one audio segment that can be:
        - an inter-pausal unit,
        - an utterance,
        - a sentence...
    no longer than a few seconds.

    Things needed to run JuliusAligner:

    To perform speech segmentation with Julius, three "models" have to be
    prepared. The models should define the linguistic property of the
    language: recognition unit, audio properties of the unit and the
    linguistic constraint for the connection between the units.
    Typically the unit should be a word, and you should give Julius these
    models below:

    1. "Acoustic model", which is a stochastic model of input waveform
    patterns, typically per phoneme. Format is HTK-ASCII model.

    2. "Word dictionary", which defines vocabulary.

    3. "Language model", which defines syntax level rules that defines the
    connection constraint between words. It should give the constraint for
    the acceptable or preferable sentence patterns. It can be:
        * either a rule-based grammar,
        * or probabilistic N-gram model.

    This class automatically construct the word dictionary and the language
    model from both:
        - the tokenization of speech,
        - the phonetization of speech.

    If outext is set to "palign", JuliusAligner will use a grammar and
    it will produce both phones and words alignments.
    If outext is set to "walign", JuliusAligner will use a slm and will
    produce words alignments only.

    """

    def __init__(self, model_dir=None):
        """Create a JuliusAligner instance.

        :param model_dir: (str) Name of the directory of the acoustic model

        """
        super(JuliusAligner, self).__init__(model_dir)

        self._extensions = ["palign", "walign"]
        self._outext = self._extensions[0]
        self._name = "julius"

    # ------------------------------------------------------------------------

    def set_outext(self, ext):
        """Set the extension for output files.

        :param ext: (str) Extension for output file name.

        """
        ext = ext.lower()
        if ext not in self._extensions:
            raise ValueError("%s is not a valid file extension for JuliusAligner" % ext)

        self._outext = ext

    # -----------------------------------------------------------------------

    def gen_slm_dependencies(self, basename, N=3):
        """Generate the dependencies (slm, dictionary) for julius.

        :param basename: (str) the base name of the slm file and of the dictionary file
        :param N: (int) Language model N-gram length.

        """
        dictname = basename + ".dict"
        slmname  = basename + ".arpa"

        phoneslist = self._phones.split()
        tokenslist = self._tokens.split()

        dictpron = sppasDictPron()

        for token, pron in zip(tokenslist, phoneslist):
            for variant in pron.split("|"):
                dictpron.add_pron(token, variant.replace("-", " "))

        if dictpron.is_unk(START_SENT_SYMBOL) is True:
            dictpron.add_pron(START_SENT_SYMBOL, SIL_PHON)
        if dictpron.is_unk(END_SENT_SYMBOL) is True:
            dictpron.add_pron( END_SENT_SYMBOL, SIL_PHON)

        dictpron.save_as_ascii(dictname, False)

        # Write the SLM
        model = sppasNgramsModel(N)
        model.append_sentences([self._tokens])
        probas = model.probabilities(method="logml")
        arpaio = sppasArpaIO()
        arpaio.set(probas)
        arpaio.save(slmname)

    # ------------------------------------------------------------------------

    def gen_grammar_dependencies(self, basename):
        """Generate the dependencies (grammar, dictionary) for julius.

        :param basename: (str) the base name of the grammar file and of the dictionary file

        """
        dictname = basename + ".dict"
        grammarname = basename + ".dfa"

        phoneslist = self._phones.split()
        tokenslist = self._tokens.split()

        tokenidx = 0
        nbtokens = len(tokenslist)-1

        with codecs.open(grammarname, 'w', sg.__encoding__) as fdfa,\
                codecs.open(dictname, 'w', sg.__encoding__) as fdict:

            for token, pron in zip(tokenslist, phoneslist):

                # dictionary:
                for variant in pron.split("|"):
                    fdict.write(str(tokenidx))
                    fdict.write(" ["+token+"] ")
                    fdict.write(variant.replace("-", " ")+"\n")

                # grammar:
                if tokenidx == 0:
                    fdfa.write("0 %s 1 0 1\n" % nbtokens)
                else:
                    fdfa.write(str(tokenidx) + " "+str(nbtokens) + " " + str(tokenidx+1) + " 0 0\n")

                tokenidx += 1
                nbtokens -= 1

            # last line of the grammar
            fdfa.write("%s -1 -1 1 0\n" % tokenidx)

    # ------------------------------------------------------------------------

    def run_julius(self, inputwav, basename, outputalign):
        """Perform the speech segmentation.
        System call to the command `julius`.

        :param inputwav: (str) the audio input file name, of type PCM-WAV 16000 Hz, 16 bits
        :param basename: (str) the base name of the grammar file and of the dictionary file
        :param outputalign: (str) the output file name

        """
        # Fix file names
        tiedlist = os.path.join(self._model, "tiedlist")
        config = os.path.join(self._model, "config")
        # Fix file names and protect special characters.
        hmmdefs = '"' + os.path.join(self._model, "hmmdefs").replace('"', '\\"') + '"'
        output = '"' + outputalign.replace('"', '\\"') + '"'
        dictionary = '"' + basename.replace('"', '\\"') + ".dict" + '"'
        grammar = '"' + basename.replace('"', '\\"') + ".dfa" + '"'
        slm = '"' + basename.replace('"', '\\"') + ".arpa" + '"'

        # the command
        command = "echo " + inputwav + " | julius "

        # the global decoding parameters
        command += " -input file -gprune safe -iwcd1 max -smpFreq 16000"
        command += ' -multipath -iwsppenalty -70.0 -spmodel "sp"'
        command += " -b 1000 -b2 1000 -sb 1000.0 -m 10000 "

        # 1. the acoustic model
        command += " -h " + hmmdefs
        if os.path.isfile(tiedlist):
            command += " -hlist " + '"' + tiedlist.replace('"', '\\"') + '"'
        if os.path.isfile(config):
            # force Julius to use configuration file of HTK, by David Yeung
            command += " -htkconf " + '"' + config.replace('"', '\\"') + '"'

        # 2. the pronunciation dictionary
        command += " -v " + dictionary

        # 3. the language model
        if self._outext == "palign":
            # grammar-based forced-alignment
            command += " -looktrellis "
            command += " -palign"
            command += " -dfa " + grammar
        else:
            # slm-based speech recognition
            command += " -silhead " + '"' + START_SENT_SYMBOL + '"'
            command += " -siltail " + '"' + END_SENT_SYMBOL + '"'
            command += " -walign "
            command += " -nlr " + slm

        # options
        if self._infersp is True:
            # inter-word short pause = on (append "sp" for each word tail)
            command += ' -iwsp'

        # output of the command
        command += " > " + output

        # Execute the command
        p = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT)
        p.wait()
        line = p.communicate()

        # Julius not installed
        if len(line[0]) > 0 and "not found" in line[0]:
            raise OSError("julius is not properly installed. See installation instructions for details.")

        # Bad command
        if len(line[0]) > 0 and "-help" in line[0]:
            raise OSError("julius command failed: %s" % " ".join(line))

        # Check output file
        if os.path.isfile(outputalign) is False:
            raise Exception("julius did not created an alignment file.")

    # ------------------------------------------------------------------------

    def run_alignment(self, input_wav, output_align, N=3):
        """Execute the external program `julius` to align.

        The data related to the unit to time-align need to be previously
        fixed with:

            - set_phones(str)
            - set_tokens(str)

        :param input_wav: (str - IN) the audio input file name, of type PCM-WAV 16000 Hz, 16 bits
        :param output_align: (str - OUT) the output file name
        :param N: (int) N value of N-grams, used only if SLM (i.e. outext=walign)

        :returns: (str) A message of `julius`.

        """
        output_align = output_align + "." + self._outext

        basename = os.path.splitext(input_wav)[0]
        if self._outext == "palign":
            self.gen_grammar_dependencies(basename)
        else:
            self.gen_slm_dependencies(basename)

        self.run_julius(input_wav, basename, output_align)
        with codecs.open(output_align, 'r', sg.__encoding__) as f:
            lines = f.readlines()

        error_lines = ""
        message = ""

        entries = []
        for line in lines:
            if line.find("Error: voca_load_htkdict") > -1 \
                    and line.find("not found") > -1:
                line = sppasUnicode(line).to_strip()
                line = line[line.find('"')+1:]
                line = line[:line.find('"')]
                if len(line) > 0:
                    entries = line.split()

        if len(entries) > 0:
            added = self.add_tiedlist(entries)
            if len(added) > 0:
                message = "The acoustic model was modified. " \
                          "The following entries were successfully added " \
                          "into the tiedlist: "
                message = message + " ".join(added) + "\n"
                self.run_julius(input_wav, basename, output_align)
                with codecs.open(output_align, 'r', sg.__encoding__) as f:
                    lines = f.readlines()

        for line in lines:
            if (line.startswith("Error:") or line.startswith("ERROR:")) \
                    and " line " not in line:
                error_lines = error_lines + line
            if "search failed" in line:
                message = "Julius has failed to find the transcription " \
                          "in the audio file. "
                error_lines = "Search error. " + error_lines

        if len(error_lines) > 0:
            raise Exception(message + error_lines)

        return message
