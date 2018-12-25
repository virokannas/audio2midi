# audio2midi
Tool for pushing audio samples through sliced FFT into polyphonic MIDI

# Example usage:
```python
python audio2midi.py samples/voice_test.wav samples/output_16chn.mid 16

# output:
# 22050 resolution length 4.16666666667 ms 91 samples
# 73235 samples 3 seconds
# frequencies divided to 18
# 5052 notes 804 ticks 3.35 seconds
```

# Sample files:
Sample output of the above example (using TAL's free NoiseMaker plug-in): https://soundcloud.com/toggleaudio/audio2midi-sample
