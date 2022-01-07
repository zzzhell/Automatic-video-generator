# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 20:54:01 2020

@author: Steinar
"""

# Search for and extract music soundtrack

from soundtrack_khinsider import search, download
import random
import re

from pydub import AudioSegment
import pyloudnorm as pyln
import soundfile as sf

def soundtrack(keyword):

    # Search for albums passing mood keyword to search function

    print('\nSearching for soundtracks containing mood keyword...\n')
    all_ids = search(keyword)
    
    all_ids_str = []
    
    # Filter away results where the mood keywords are in album title (single songs wanted)
    
    for i, s in enumerate(all_ids):
        sid = all_ids[i].id
        all_ids_str.append(sid)

    # Tokenize album titles
    
    album_title_tokens = [title.replace('-', ' ').split(' ') for title in all_ids_str]
          
    for s in album_title_tokens:
        for i, ss in enumerate(s):
            if re.search(keyword, ss, re.IGNORECASE):
                album_title_tokens.pop(i) # Remove matches in album title instead of track
                all_ids.pop(i)
    
    # Pick one album among them

    single_id = random.sample(all_ids, 1)
    single_id_string = single_id[0].id
    print('Album title:', (single_id_string))
    
    # Get song objects from album and get song titles as strings

    print('\nExtracting song metadata...\n')
    song_obj_list = single_id[0].songs
    
    # song_title_strs = []
    song_hits = []
    song_hits_idx = []

    for o in song_obj_list:
        s = o.name
        print(s)
        ss = s.split()
        for sss in ss:
            if re.search(keyword, sss, re.IGNORECASE):
                song_hits.append(s)
                song_hits_idx.append(i)
                break
        if len(song_hits) == 1:
            break
        
    print('\nTrack title:', (song_hits))
        
    song_hit_idx = random.sample(song_hits_idx, 1)
    song_hit_obj = song_obj_list[song_hit_idx[0]]
    
    # Download song
    
    print('\nExtracting song...\n')
    
    download(single_id_string, song_hit_obj, path="c:/Users/pokal/AVFALL/aaaavg/st_mp3",
             makeDirs=True, formatOrder=None, verbose=False)
        
    hit_file_obj = song_obj_list[song_hits_idx[0]].files
    
    song_fname_str = hit_file_obj[0].filename
    
    return song_fname_str

# Measure and modify soundtrack loudness using LUFS (loudness units relative to full scale)

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