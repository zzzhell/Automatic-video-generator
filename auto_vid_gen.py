# from tqdm import tqdm

from vid_analysis import check, find_stats, tc_from_csv
from vid_search import get_filenames
from vid_timecode import moviepy_tc
from voiceover_text import keyword_to_voice, map_range
from soundtrack import soundtrack
from soundtrack_loudness import lufs

from internetarchive import download
import argparse
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips
from moviepy.audio.fx.volumex import volumex

import random
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from statistics import mean

import os

# Command line arguments. Create parser, add arguments and execute parse_args() method

my_parser = argparse.ArgumentParser(description='Automatically generates a video with music and synthetic voiceover. \
                                                Using three sets of input search terms, the program extracts, analyzes, \
                                                edits and combines videos, voiceover texts and music from the Internet \
                                                Archive and KHInsider.')

# my_parser.add_argument('vkw',
#                         type=str,
#                         help=""" "Your video search keywords" """)

# vkw_parse = my_parser.parse_args()
# vkw_dict = vars(vkw_parse)
# vkw_arg = vkw_dict['vkw']

# Instead of command line keyword arguments

vkw_arg = 'fast racing car' # Video search phrase
vo_kw = 'racing' # Voiceover text search keyword
st_kw = 'ominous' # Soundtrack search keyword

vkw_arg = vkw_arg.split() # Split search phrase keywords
vkw_name = '_'.join(vkw_arg) # Add search phrase to file name
or_op = ' OR ' # Each element of the search phrase is separated by OR
vkw_arg = or_op.join(vkw_arg)

# Initialize content analysis value and index lists

cont_candidate_val = [0, 0]
cont_candidate_vals = []
cont_candidate_ins = []
cont_candidate_outs = []
framerates = []

num_vids = 2
num_clips = 8 # Number of clips to cut from each video

# Video download using Internet Archive and content analysis using PySceneDetect
# Iterate while video HSL values are too low or not enough scenes

while check(cont_candidate_val, 5) and len(cont_candidate_val) <= num_clips-1 and len(framerates) < num_vids:
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
        if len(scene_list_frames) == 1:
           scene_list_frames.append(500)
           break
        cont_candidate_in, cont_candidate_out, framerate, cont_candidate_val = tc_from_csv(str_fnames, scene_list_frames, num_clips)
        if check(cont_candidate_val, 5):
            print('Content values too low. Extracting different videos...\n')
            framerates = []
            break
        # elif len(cont_candidate_val) <= num_clips-1:
        #     print('Not enough scenes. Extracting different videos...\n')
        #     framerates = []
        #     break
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

# Create video file clip objects from video files. Resize them to the same size

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
    #clips.append(temp_clips)

# Shuffle clips and concatenate into output video

random.shuffle(clips)
videoclip = concatenate_videoclips(clips, method='compose')
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

# cont_avg = temp_avg / len(cont_candidate_vals)

voice_rate = round(map_range(cont_avg, 5, 100, 200, 60))

# Generate voiceover audio file

script = keyword_to_voice(vo_kw, 6, voice_rate)
voiceover_file = '{0}.mp3'.format(vo_kw)
vo_clip = AudioFileClip(voiceover_file)
vo_duration = vo_clip.duration # Get voiceover clip duration

# Extract music soundtrack

soundtrack_fname = soundtrack(st_kw)
soundtrack_path = 'c:/Users/pokal/AVFALL/avg/{0}'.format(soundtrack_fname)
soundtrack_clip = AudioFileClip(soundtrack_path)
st_clip_gain = volumex(soundtrack_clip, 0.25) # Gain level of music
st_clip_duration = soundtrack_clip.duration

# Set duration of video and soundtrack clips to voiceover duration

st_clip_pre = st_clip_gain.set_duration(vo_duration)

if vid_clip_duration < vo_duration:
    videoclips = [videoclip, videoclip]
    vid_clips = concatenate_videoclips(videoclips, method='compose')
    vid_clip = vid_clips.set_duration(vo_duration)
else:
    vid_clip = videoclip.set_duration(vo_duration)        

# Measure and modify soundtrack loudness using LUFS (loudness units relative to full scale)

print('Converting soundtrack audio to measure loudness...\n')

st_pre_path = 'pre_lufs_{0}'.format(soundtrack_fname)
AudioFileClip.write_audiofile(st_clip_pre, st_pre_path) # Write soundtrack mp3 with new duration
lufs(st_pre_path, st_kw, soundtrack_fname)
st_post_path = 'post_lufs_{0}'.format(soundtrack_fname)
st_clip = AudioFileClip(st_post_path) # Modified mp3 to object

# Add music clip to voiceover clip

vo_st_clip = CompositeAudioClip([vo_clip, st_clip])

# Find sentiment of script

analyzer = SentimentIntensityAnalyzer()
sent_dict = analyzer.polarity_scores(script)
print(sent_dict)

# Add audio clip to video clip

outclip = vid_clip.set_audio(vo_st_clip)

# Add voiceover and soundtrack keywords to output file name

vid_vo_st_kw = [vkw_name, vo_kw, st_kw]
outfile_name = '-'.join(vid_vo_st_kw)

# Save video file

outfile = outclip.write_videofile("{0}_01.mp4".format(outfile_name))

allclips = [*vids, *clips, vid_clip, vo_clip, st_clip, vo_st_clip, outclip]

# Close audio and video clips

for openclip in allclips:
    openclip.close()
    
# Remove temporary video and audio files

if os.path.isfile(voiceover_file):
    os.remove(voiceover_file)
# if os.path.isfile(soundtrack_path): # Pydub does not close file
  #  os.remove(soundtrack_path)
if os.path.isfile(st_pre_path):
    os.remove(st_pre_path)    
if os.path.isfile(st_post_path):
    os.remove(st_post_path)
if os.path.isfile(fnames_2dl[0]):
    os.remove(fnames_2dl[0])
if os.path.isfile(fnames_2dl[1]):
    os.remove(fnames_2dl[1])