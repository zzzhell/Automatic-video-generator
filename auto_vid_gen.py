# -*- coding: utf-8 -*-
"""
@author: Steinar
"""

from vid_search import get_filenames
from vid_analysis import check, find_stats, tc_from_csv, moviepy_tc
from voiceover import keyword_to_voice, map_range
from soundtrack import soundtrack, lufs

from internetarchive import download
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips
from moviepy.audio.fx.volumex import volumex

import random
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from statistics import mean

import os

# Search phrase as string

vkw_arg = 'amazing skydiving lottery' # Video search phrase
vkw_split = vkw_arg.split()
vo_kw = random.sample(vkw_split, 2) # Pick two words for voiceover search

vkw_arg = vkw_arg.split() # Split search phrase keywords
vkw_name = '_'.join(vkw_arg) # Add search phrase to file name
or_op = ' OR ' # Each element of the search phrase is separated by OR
vkw_arg = or_op.join(vkw_arg)

# Uncomment to use command line argument parser instead of the section above

#import argparse

# my_parser = argparse.ArgumentParser(description='Automatically generates a video with music and synthetic voiceover. \
#                                                 Using the input search phrase argument, the program extracts, analyzes, \
#                                                 edits and combines videos, voice-over texts and music from the Internet \
#                                                 Archive and KHInsider.')

# my_parser.add_argument('vkw',
#                         type=str,
#                         help=""" "Your video search keywords" """)

# vkw_parse = my_parser.parse_args()
# vkw_dict = vars(vkw_parse)
# vkw_arg = vkw_dict['vkw']

# Initialize content analysis value and index lists

cont_candidate_val = [0, 0]
cont_candidate_vals = []
cont_candidate_ins = []
cont_candidate_outs = []
framerates = []

num_vids = 2
num_clips = 8 # Number of clips to cut from each video
cont_thresh = 5

# Video download using Internet Archive and content analysis using PySceneDetect
# Iterate while video HSL values are too low or not enough scenes

while check(cont_candidate_val, cont_thresh) and len(cont_candidate_val) <= num_clips-1 and len(framerates) < num_vids:
    cont_candidate_val = [0, 0]
    cont_candidate_vals = []
    cont_candidate_ins = []
    cont_candidate_outs = []
    rand_ident = []
    fnames_2dl = []
    print('Extracting video metadata...\n')
    rand_ident, fnames_2dl = get_filenames(vkw_arg, num_vids)
    print('Extracting video files...\n', flush=True)
    for ident, fname in zip(rand_ident, fnames_2dl):
        download(ident, files=fname, return_responses=False, no_directory='true')
    print('Analyzing video content...\n')
    for name in range(0, len(fnames_2dl)):
        scene_list_frames = find_stats(fnames_2dl[name])
        str_fnames = str(fnames_2dl[name]).strip("['']")
        cont_candidate_in, cont_candidate_out, framerate, cont_candidate_val = tc_from_csv(str_fnames, scene_list_frames, num_clips)
        if check(cont_candidate_val, cont_thresh):
            print('Content values too low. Extracting different videos...\n')
            framerates = []
            break
        else:
            print('Videos analyzed. Timecodes appended to list.\n')
            cont_candidate_ins.append(cont_candidate_in)
            cont_candidate_outs.append(cont_candidate_out)
            cont_candidate_vals.append(cont_candidate_val)
            framerates.append(framerate)
            
# Calculate timecode in the format MoviePy wants

mp_tc_ins = []
mp_tc_outs = []

for tc_in, tc_out in zip(cont_candidate_ins, cont_candidate_outs):
    mp_tc_in, mp_tc_out = moviepy_tc(tc_in, tc_out, framerate)
    mp_tc_ins.append(mp_tc_in)
    mp_tc_outs.append(mp_tc_out)

# Create video file clip objects from video files

vid1 = VideoFileClip(fnames_2dl[0])
vid2 = VideoFileClip(fnames_2dl[1])
vids = [vid1, vid2]

if 2 < len(fnames_2dl):
    vid3 = VideoFileClip(fnames_2dl[2])
    vids = [vid1, vid2, vid3]

# Cut extracted videos into clips

clips = []

print('Cutting video...\n', flush=True)

for vid, tc_list_in, tc_list_out in zip(vids, mp_tc_ins, mp_tc_outs):
    for tc_in, tc_out in zip(tc_list_in, tc_list_out):
        clip = vid.subclip(tc_in, tc_out)
        clips.append(clip)

# Shuffle clips and concatenate into output video

random.shuffle(clips)
videoclip = concatenate_videoclips((clips), method='compose')
vid_clip_duration = videoclip.duration # Get video clip duration

# Map average content values to voiceover speech rate

sum = 0
temp_avg = []

for sub in cont_candidate_vals: 
    for i in sub: 
        sum = sum + i
        temp = sum / len(sub)
        temp_avg.append(temp)

cont_avg = round(mean(temp_avg))

voice_rate = round(map_range(cont_avg, cont_thresh, 100, 200, 60))

# Generate voiceover audio file

script, vo_file = keyword_to_voice(vo_kw, 6, voice_rate)
vo_clip = AudioFileClip(vo_file)
vo_duration = vo_clip.duration # Get voiceover clip duration

# Find sentiment of script

analyzer = SentimentIntensityAnalyzer()
sent_dict = analyzer.polarity_scores(script)
print(sent_dict)
sent_comp = list(sent_dict.values())[3] # Compound score

# Map sentiment compound score to circumplex model

cv_upper = 1
cv_lower = -1

# 20 emotional levels with values and strings on circumplex model

circumplex_values = [-1 + x*(cv_upper-cv_lower)/20 for x in range(20)]

circumplex_strings = [['alarm', 'panic', 'horror'], ['afraid', 'scary', 'fright'],  ['angry', 'furious', 'outrage'],
                      ['nervous', 'stress', 'spook'], ['tense', 'concern', 'jitter'], ['distress', 'irritation',
                      'upset', 'agitation'], ['gloomy', 'bleak', 'somber'], ['depression', 'melancholy'],
                      ['boring', 'tiresome', 'tedious'], ['tired', 'exhausted'], ['sleepy'], ['relax'],
                      ['serene', 'smooth'], ['satisfied', 'fulfilled'], ['pleased', 'content'], ['happy', 'delight'],
                      ['cheerful', 'joyful'], ['excited'], ['astonish'], ['ecstasy', 'euphoria']]

# Find compound value level on circumplex model

for i, val in enumerate(circumplex_values):
    while sent_comp > val:
        st_kws = circumplex_strings[i]
        break

# Extract music soundtrack using mood string as search term

st_clip_duration = 0

while st_clip_duration < vo_duration:
    print('\nSoundtrack too short:', st_clip_duration)
    st_kw = str(random.sample(st_kws, 1)).strip("['']") # Pick one of the mood synonyms from the same level
    print('\nMood keyword from text analysis:', st_kw)
    soundtrack_fname = soundtrack(st_kw)
    soundtrack_path = 'c:/Users/pokal/AVFALL/aaaavg/st_mp3/{0}'.format(soundtrack_fname)
    soundtrack_clip = AudioFileClip(soundtrack_path)
    st_clip_duration = soundtrack_clip.duration

st_clip_gain = volumex(soundtrack_clip, 0.25) # Gain level of music

# Set duration of video and soundtrack clips to voiceover duration

st_clip_pre = st_clip_gain.set_duration(vo_duration)

if vid_clip_duration < vo_duration:
    videoclips = [videoclip, videoclip]
    vid_clips = concatenate_videoclips(videoclips, method='compose')
    vid_clip = vid_clips.set_duration(vo_duration)
else:
    vid_clip = videoclip.set_duration(vo_duration)        

# st_clip_pre = st_clip_gain
# vid_clip = videoclip

# Measure and modify soundtrack loudness using LUFS (loudness units relative to full scale)

print('Converting soundtrack audio to measure loudness...\n')

st_pre_path = 'pre_lufs_{0}'.format(soundtrack_fname)
AudioFileClip.write_audiofile(st_clip_pre, st_pre_path) # Write soundtrack mp3 with new duration
lufs(st_pre_path, st_kw, soundtrack_fname)
st_post_path = 'post_lufs_{0}'.format(soundtrack_fname)
st_clip = AudioFileClip(st_post_path) # Modified mp3 to object

# Add music clip to voiceover clip

vo_st_clip = CompositeAudioClip([vo_clip, st_clip])

# Add audio clip to video clip

outclip = vid_clip.set_audio(vo_st_clip)

# Add voiceover and soundtrack keywords to output file name

vo_kw = '_'.join(vo_kw)
vid_vo_st_kw = [vkw_name, vo_kw, st_kw]
outfile_name = '-'.join(vid_vo_st_kw)

# Save video file

outfile = outclip.write_videofile("{0}_02.mp4".format(outfile_name))

allclips = [*vids, *clips, vid_clip, vo_clip, st_clip, vo_st_clip, outclip]

# Close audio and video clips

for openclip in allclips:
    openclip.close()
    
# Remove temporary video and audio files

if os.path.isfile(vo_file):
    os.remove(vo_file)
#if os.path.isfile(soundtrack_path): # Pydub does not close file
#    os.remove(soundtrack_path)
if os.path.isfile(st_pre_path):
    os.remove(st_pre_path)    
if os.path.isfile(st_post_path):
    os.remove(st_post_path)
if os.path.isfile('pre_lufs_{0}.wav'.format(st_kw)):
    os.remove('pre_lufs_{0}.wav'.format(st_kw))
if os.path.isfile('post_lufs_{0}.wav'.format(st_kw)):
    os.remove('post_lufs_{0}.wav'.format(st_kw))
if os.path.isfile(fnames_2dl[0]):
    os.remove(fnames_2dl[0])
if os.path.isfile(fnames_2dl[1]):
    os.remove(fnames_2dl[1])