# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 19:48:49 2020

@author: Steinar
"""

import pickle
import random
import pyttsx3

# Open dataset stored as pickle file where sentences are already split into lists

with open('sentences.pickle', 'rb') as f:
    sentences = pickle.load(f)

def keyword_to_voice(text_search_keyword, num_sentences, voice_rate):

    hits = []
    next_hits = []
    hitidx = []
    next_hit_idx = []
    next_hit_idxs = []
        
    engine = pyttsx3.init() # Define voiceover engine
    
    # Collect all sentences containing search keyword
    
    for i, s in enumerate(sentences):
            if text_search_keyword in s:
                  hits.append(s) # Sentence containing keyword
                  hitidx.append(i)
                  next_hit = sentences[i:i+num_sentences] # Sentences following it
                  next_hits.append(next_hit)
                  next_hit_idx = [*range(i, i+num_sentences)]
                  next_hit_idxs.append(next_hit_idx)
    
    # Remove sentences that are split by line break hypenation
    
    for i, hitlist in enumerate(next_hits):
        for idx, hit in enumerate(hitlist):
            if '¬' in hit:
                next_hits.pop(idx) # Removes whole list, although hypenation only would be optimal
                next_hit_idxs.pop(idx)
                
    # Join lists of strings (single words) into sentence strings
    
    hit_sentences = []
    
    rand_sentences = random.sample(next_hits, 1)
    
    for i, hitlist in enumerate(rand_sentences):
        for idx, hit in enumerate(hitlist):
            hit_single = " ".join([rand_sentences][0][i][idx])
            hit_sentences.append(hit_single)
        
    script = ' '.join(hit_sentences)
    
    # Send manuscript to voice synthesizer
    engine.setProperty('rate', voice_rate)    
    voices = engine.getProperty('voices')       # Get details of current voice
    #engine.setProperty('voice', voices[0].id)  # Changing index changes voice
    engine.setProperty('voice', voices[1].id)
    engine.setProperty('volume', 1.5)
    
    print('Generating voiceover manuscript and saving audio file... \n')
    print('Voiceover speaking rate is:', (voice_rate))
        
    engine.save_to_file(script, '{0}.mp3'.format(text_search_keyword))
    engine.runAndWait()
    engine.stop()

    return script

# Map one range of values to another (to determine speech rate)

def map_range(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)
