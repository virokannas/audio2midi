#!/usr/bin/env python
#
# Requirements: python-midi, scipy
#

import sys
import os
try:
    from midiutil.MidiFile import MIDIFile
except:
    print("Sorry, audio2midi requires midiutil, please install it first!")
    print("    pip install midiutil")
    print("")
    sys.exit(1)

import math
try:
    from scipy.io import wavfile
    from scipy.fftpack import fft, fftfreq
except:
    print("Sorry, audio2midi requires scipy, please install it first!")
    print("    pip install scipy")
    print("")
    sys.exit(1)

if len(sys.argv) < 3:
    print("Usage: ")
    print("    audio2midi.py <input.wav> <output.mid> [polyphony]")
    print("")
    print("Optional:")
    print("    polyphony - how many concurrent frequencies the synth can handle")
    print("")
    sys.exit(1)

source_file = sys.argv[1]
output_file = sys.argv[2]
polyphony = 4
if len(sys.argv) > 3:
    polyphony = int(sys.argv[3])

sampFreq, snd = wavfile.read(sys.argv[1])

# you can adjust BPM to match with your project to try to match the MIDI timing
BPM = 120.0
RESOLUTION=1
MIDI_RES=60
TICK_LENGTH = (60000.0 / (BPM * (MIDI_RES / RESOLUTION)))
SLICE_LENGTH = int(sampFreq * TICK_LENGTH / 1000.0)
print sampFreq, "resolution length",TICK_LENGTH,"ms"

def file2fftmidi(mf, x):
    t=0
    t_len = len(snd)
    print t_len,"samples",(t_len / sampFreq),"seconds"
    t_tot = 0
    slc = SLICE_LENGTH
    nts = 0
    freqs = fftfreq(slc, 1.0/sampFreq)
    while t_tot + slc < t_len:
        data = abs(fft(snd[t_tot:(t_tot+slc)]))
        tot = 0

        # find top x frequencies
        top_freqs = data.argsort()[-x:][::-1]
        for tfs in top_freqs:
            freq = freqs[tfs]
            smp_data = data[tfs]
            ons = []
            if smp_data > 100.0 and freq > 0.0:
                ptc = int(12.0 * math.log(float(freq)/440.0, 2.0)) + 69
                if ptc<0 or ptc>127:
                    continue
                vel = min(int(smp_data * 128.0/1000000.0),127)
                if vel > 0:
                    mf.addNote(0, 0, ptc, t*RESOLUTION, RESOLUTION, vel)
                    nts+=1
        t_tot += slc
        t+=1
    print nts,"notes",t,"ticks",t*(TICK_LENGTH/ 1000.0),"seconds"
    return t

mf = MIDIFile(1, eventtime_is_ticks=True, ticks_per_quarternote=MIDI_RES)
mf.addTrackName(0, 0, "{}".format(os.path.basename(sys.argv[1])))
mf.addTempo(0, 0, BPM)

file2fftmidi(mf, polyphony)
with open(output_file, 'wb') as output_file:
    mf.writeFile(output_file)

