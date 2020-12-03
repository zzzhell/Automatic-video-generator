# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 17:52:05 2020

@author: Steinar
"""

# Convert timecode to the format MoviePy wants

def moviepy_tc(cont_candidate_in, cont_candidate_out, framerate):

    mp_tc_in = []
    mp_tc_out = []

    for frames in cont_candidate_in:
        frames = frames/framerate
        mp_tc_in.append(round(frames, 2))
         
    for frames in cont_candidate_out:
        frames = frames/framerate
        frames = frames-1 # Compensate for drop frames
        mp_tc_out.append(round(frames, 2))
        
    return mp_tc_in, mp_tc_out