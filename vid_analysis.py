# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 12:15:41 2020

@author: PySceneDetect, Steinar
"""

from scenedetect.video_manager import VideoManager
from scenedetect.scene_manager import SceneManager
from scenedetect.stats_manager import StatsManager # For caching detection metrics and saving/loading to a stats file
from scenedetect.detectors.content_detector import ContentDetector # For content-aware scene detection

import os.path

import csv

def check(list_, val): # For checking content values and number of scenes
    for x in list_:
        if val < x:
            return False
    return True

# Content analysis using PySceneDetect

def find_stats(video_path):
    # type: (str) -> List[Tuple[FrameTimecode, FrameTimecode]]
    video_manager = VideoManager([video_path])
    stats_manager = StatsManager()
    # Construct our SceneManager and pass it our StatsManager.
    scene_manager = SceneManager(stats_manager)

    # Add ContentDetector algorithm (each detector's constructor
    # takes detector options, e.g. threshold).
    scene_manager.add_detector(ContentDetector(threshold=30.0))
    base_timecode = video_manager.get_base_timecode()

    # We save our stats file to {VIDEO_PATH}.stats.csv.
    stats_file_path = '%s.stats.csv' % video_path

    scene_list = [] #

    try:
        # If stats file exists, load it.
        if os.path.exists(stats_file_path):
            # Read stats from CSV file opened in read mode:
            with open(stats_file_path, 'r') as stats_file:
                stats_manager.load_from_csv(stats_file, base_timecode)

        # Set downscale factor to improve processing speed.
        video_manager.set_downscale_factor()

        # Start video_manager.
        video_manager.start()

        # Perform scene detection on video_manager.
        scene_manager.detect_scenes(frame_source=video_manager)

        # Obtain list of detected scenes.
        scene_list = scene_manager.get_scene_list(base_timecode)
        # Each scene is a tuple of (start, end) FrameTimecodes.
        
        #scene_manager.write_scene_list('%s.scenes.csv', scene_list, cut_list=None)
        
        tc_frame_list = []
        
        for i, scene in enumerate(scene_list):
                frame = scene[0].get_frames()
                tc_frame_list.append(frame)
            
        # # We only write to the stats file if a save is required:
        if stats_manager.is_save_required():
            with open(stats_file_path, 'w') as stats_file:
                stats_manager.save_to_csv(stats_file, base_timecode)

    finally:
        video_manager.release()

    return tc_frame_list #

# Get timecodes and content values from .csv

def tc_from_csv(video_path, scene_list_frames, num_clips):
    
    with open('{0}.stats.csv'.format(video_path), newline='') as statsf:
        reader = csv.reader(statsf)
        #framerate = [row.split()[0] for row in statsf]
        #dreader = csv.DictReader(statsf)
        #framerate = float(dreader.fieldnames[1])
        next(reader)
        headers = next(reader)
        # Transpose the data --> columns become rows and rows become columns
        data = zip(*reader)
        # Create a dictionary by combining the headers with the data
        content_dict = dict(zip(headers, data))
    
    with open('{0}.stats.csv'.format(video_path), newline='') as statsf:
        reader = csv.DictReader(statsf)
        framerate = float(reader.fieldnames[1])
    
    entries_to_remove = ('delta_hue','delta_lum','delta_sat','Frame Number')
    for k in entries_to_remove:
        content_dict.pop(k, None)
    
    content_val = list(map(float, content_dict['content_val']))
    # content_tc = list(list(content_dict['Timecode']))
    
    print('\nFinding scenes with highest average HSL values...\n', flush=True)
    
    cont_val_periods = [content_val[i:j] for i, j in zip([0]+scene_list_frames, scene_list_frames+[None])]
    cont_val_periods.pop(0)
    cont_val_periods.pop(-1)
    
    cont_period_avgs = [float(sum(row)/len(row)) for row in cont_val_periods]
    
    cont_candidates = sorted([(x,i) for (i,x) in enumerate(cont_period_avgs)], reverse=True) [:num_clips]
    cont_candidate_vals, cont_cand_in_idx = list(zip(*cont_candidates))
    cont_cand_in_idx = list(cont_cand_in_idx)
    cont_cand_out_idx = [x+1 for x in cont_cand_in_idx]
    
    # Get matching frame indices from full list of frames 
    
    cont_candidate_in = [scene_list_frames[i] for i in cont_cand_in_idx]
    cont_candidate_out = [scene_list_frames[i] for i in cont_cand_out_idx]

    # Remove CSV stats file
    
    if os.path.isfile('{0}.stats.csv'.format(video_path)):
        os.remove('{0}.stats.csv'.format(video_path))
  
    return cont_candidate_in, cont_candidate_out, framerate, cont_candidate_vals