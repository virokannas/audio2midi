#!/usr/bin/env python
#
# Requirements: python-midi, scipy
#

import sys
try:
    import midi
except:
    print("Sorry, audio2midi requires python-midi, please install it first!")
    print("    pip install python-midi")
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

def file2fftmidi(track, x):
    t=0
    # splice audio file per 100 bytes
    t_len = len(snd)
    t_tot = 0
    slc = 96
    max_data = max(abs(fft(snd)))
    freqs = fftfreq(slc, 1.0/sampFreq)
    while t_tot + slc < t_len:
        data = abs(fft(snd[t_tot:t_tot+slc]))
        tot = 0

        # find top x frequencies
        top_freqs = data.argsort()[-x:][::-1]
        for tfs in top_freqs:
            freq = freqs[tfs]
            smp_data = data[tfs]
            if smp_data > 10.0 and freq > 0.0:
                ptc = int(12.0*math.log(float(freq)/440.0, 2.0))+69
                vel = min(int(smp_data * 128.0 / 1000000.0),127)
                on=midi.NoteOnEvent(tick=0, velocity=vel, pitch=ptc)
                off=midi.NoteOffEvent(tick=1, pitch=ptc)
                track.append(on)
                track.append(off)

        t_tot += slc
        t+=1
    return t

pattern = midi.Pattern(tick_relative=False)
track = midi.Track(tick_relative=False)
pattern.append(track)

file2fftmidi(track, polyphony)

eot = midi.EndOfTrackEvent(tick=1)
track.append(eot)
midi.write_midifile(output_file, pattern)
