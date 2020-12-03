# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 20:54:01 2020

@author: Steinar
"""

# Search for and extract music soundtrack

from soundtrack_khinsider import search, download
import random

def soundtrack(input_keyword):

    # Keyword variations

    lower_kw = input_keyword # Lowercase
    cap_kw = input_keyword.capitalize() # Capitalized
    upper_kw = input_keyword.upper() # All caps
    plur_kw = input_keyword + 's' # Plural
    
    # Search for albums passing mood keyword to search function

    print('\nSearching for soundtracks containing mood keyword...\n')
    all_ids = search(input_keyword)
    
    all_ids_str = []
    
    # Filter results where the mood keywords are in album title (single songs wanted)
    
    for i, s in enumerate(all_ids):
        sid = all_ids[i].id
        all_ids_str.append(sid)
    
    # Tokenize album titles
    
    album_title_tokens = [title.replace('-', ' ').split(' ') for title in all_ids_str]
    
    for i, s in enumerate(album_title_tokens):
        if lower_kw in s: # If lowercase
            album_title_tokens.pop(i)    
            all_ids.pop(i)
    
    for i, s in enumerate(album_title_tokens):
        if cap_kw in s:  # If capitalized
            album_title_tokens.pop(i)      
            all_ids.pop(i)
            
    for i, s in enumerate(album_title_tokens):
        if upper_kw in s: # If all caps
            album_title_tokens.pop(i)
            all_ids.pop(i)
            
    for i, s in enumerate(album_title_tokens):
        if plur_kw in s: # If all caps
            album_title_tokens.pop(i)
            all_ids.pop(i)
    
    # Pick one album among them

    single_id = random.sample(all_ids, 1)
    single_id_string = single_id[0].id
    print('Album title:', (single_id_string))
    
    # Get song objects from album and get song titles as strings

    print('\nExtracting song metadata...\n')
    song_obj_list = single_id[0].songs
    
    song_title_strs = []
    
    for o in song_obj_list:
        s = o.name
        song_title_strs.append(s)
    
    # Tokenize song titles so single words can be found

    print('Finding song containing mood keyword...\n')
    song_title_tokens = [title.split() for title in song_title_strs] 
    
    # Find song titles that match the keyword

    song_hits = []
    song_hits_idx = []
    
    for i, s in enumerate(song_title_tokens):
             if cap_kw in s:  # If capitalized
                   song_hits.append(s)
                   song_hits_idx.append(i)
             if lower_kw in s: # If lowercase
                   song_hits.append(s)
                   song_hits_idx.append(i)
             if upper_kw in s: # If all caps
                   song_hits.append(s)
                   song_hits_idx.append(i)
             if plur_kw in s:
                   song_hits.append(s)
                   song_hits_idx.append(i)
                   
    print('Track title:', (song_hits))
    # print('All tracks:', (song_title_tokens))
    
    song_hit_idx = random.sample(song_hits_idx, 1)
    song_hit_obj = song_obj_list[song_hit_idx[0]]
    
    # Download song
    
    print('Extracting song...\n')
    
    download(single_id_string, song_hit_obj, path="c:/Users/pokal/AVFALL/avg",
             makeDirs=True, formatOrder=None, verbose=False)
        
    hit_file_obj = song_obj_list[song_hits_idx[0]].files
    
    song_fname_str = hit_file_obj[0].filename
    
    return song_fname_str