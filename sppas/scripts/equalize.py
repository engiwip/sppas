from argparse import ArgumentParser
import os
import sys


PROGRAM = os.path.abspath(__file__)
WAVETOASTER = os.path.join(os.path.dirname( os.path.dirname( PROGRAM ) ))
SRC = os.path.join(WAVETOASTER, "src" )
sys.path.append(SRC)

import audiodata
from audiodata.channelsequalizer import ChannelsEqualizer
from audiodata.audio import AudioPCM

sys.path.remove(SRC)

parser = ArgumentParser(usage="%s -w input files [options]" % os.path.basename(PROGRAM), description="A script to equalize the number of frames of audio files")

parser.add_argument("-w", metavar="file", nargs='+', required=True,  help='Audio Input file names')


# ----------------------------------------------------------------------------

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------


equalizer = ChannelsEqualizer()

file = audiodata.open(args.w[0])
sampwidth = file.get_sampwidth()
framerate = file.get_framerate()

for inputFile in args.w:
    audio = audiodata.open(inputFile)
    if audio.get_sampwidth() != sampwidth:
        print "Input files must have the same sample width !"
        sys.exit(1)
    if audio.get_framerate() != framerate:
        print "Input files must have the same framerate !"
        sys.exit(1)
    idx = audio.extract_channel(1)
    equalizer.append_channel(audio.get_channel(idx))

equalizer.equalize()

# Save the converted channel
for i, chan in enumerate(equalizer.channels):
    audio_out = AudioPCM()
    audio_out.append_channel( chan )
    filename, extension = os.path.splitext(args.w[i])
    audiodata.save(filename + "EQUAL" + extension, audio_out)

# ----------------------------------------------------------------------------