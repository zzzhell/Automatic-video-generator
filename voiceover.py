# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 19:48:49 2020

@author: Steinar
"""

import pickle
import random
import pyttsx3
import re

# Open dataset stored as pickle file where sentences are already split into lists

with open('sentences.pickle', 'rb') as f:
    sentences = pickle.load(f)

def keyword_to_voice(keywords, num_sentences, voice_rate):

    hits = []
   
    engine = pyttsx3.init() # Define voiceover engine
    
    # Collect sentences containing first search keyword and the sentences following it
    
    for i, sent in enumerate(sentences):
        for idx, s in enumerate(sent):
            if re.search(keywords[0], s, re.IGNORECASE):
                  hit = sentences[i:i+num_sentences] # Sentences following match
                  hits.append(hit)
            
    # Second keyword within sentences collected above
    
    for h in hits:
        for hh in h:
            for hhh in hh:
                if re.search(keywords[1], hhh, re.IGNORECASE):
                    hits = []
                    hits.append(h)

    # Remove sentences that are split by line break hypenation
    
    for hitlist in hits:
        for hit in hitlist:
            for iii, h in enumerate(hit):
                if re.search('¬', h):
                    hit.pop(iii)
                    
    # Join lists of strings (single words) into sentence strings
    
    hit_sentences = []
    
    rand_sentences = random.sample(hits, 1)
    
    for i, hitlist in enumerate(rand_sentences):
        for idx, hit in enumerate(hitlist):
            hit_single = " ".join([rand_sentences][0][i][idx])
            hit_sentences.append(hit_single)
        
    script = ' '.join(hit_sentences) # Join sentence strings into a single string
    
    # Voice synthesizer properties
    
    engine.setProperty('rate', voice_rate)    
    voices = engine.getProperty('voices')       # Get details of current voice
    #engine.setProperty('voice', voices[0].id)  # Changing index changes voice
    engine.setProperty('voice', voices[1].id)
    engine.setProperty('volume', 1.5)
    
    print('Generating voiceover manuscript and saving audio file... \n')
    print('Voiceover speaking rate is:', (voice_rate))
    
    vo_file = '{0}_{1}.mp3'.format(keywords[0], keywords[1])
    engine.save_to_file(script, vo_file) # Send manuscript to voice
    engine.runAndWait()
    engine.stop()

    return script, vo_file

# Map one range of values to another (to determine speech rate)

def map_range(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    
    return rightMin + (valueScaled * rightSpan)