# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 17:28:27 2020

@author: Steinar
"""

# Measure and modify soundtrack loudness using LUFS (loudness units relative to full scale)

from pydub import AudioSegment
import pyloudnorm as pyln
import soundfile as sf

def lufs(soundtrack_path, st_kw, soundtrack_fname):

    # Audio has to be converted from mp3 to wav before measuring and processing
    
    st_mp3 = AudioSegment.from_mp3(soundtrack_path)
    st_wav_pre = 'pre_lufs_{0}.wav'.format(st_kw)
    st_mp3.export(st_wav_pre, format="wav") # Write wav
    
    data, rate = sf.read(st_wav_pre) # Load audio (with shape (samples, channels))
    meter = pyln.Meter(rate) # Create BS.1770 meter

    loudness = meter.integrated_loudness(data) # Measure loudness

    print('Soundtrack loudness in dB LUFS:', loudness)
    
    print('\nNormalizing soundtrack loudness to -28 dB LUFS...\n')
    loudness_normalized_audio = pyln.normalize.loudness(data, loudness, -28.0)

    st_wav_post = 'post_lufs_{0}.wav'.format(st_kw)
    
    sf.write(st_wav_post, loudness_normalized_audio, rate)
    
    st_wav_lufs = AudioSegment.from_wav(st_wav_post)
    
    st_wav_lufs.export('post_lufs_{0}'.format(soundtrack_fname), format="mp3")