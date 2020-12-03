# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 12:43:33 2020

@author: Steinar
"""

from internetarchive import search_items, get_item
import random

def get_filenames(video_search_keyword, number_of_videos):
    ''' Search query returns items to list. Only unrestricted items between
    30 and 70 MB. ''' 

    search_results = []
    num_of_items = 50
    
    #, "formats":"h.264"
    
    # for i in tqdm(range(num_of_items)):
    for item in search_items('{0} AND mediatype:movies \
                                 AND NOT access-restricted-item:true \
                                 AND NOT funny_or_die \
                                 AND NOT g4tv.com \
                                 AND NOT epicmealtime \
                                 AND item_size:[30000000 TO 70000000]'
                                 .format(video_search_keyword), params={"page":"1","rows":num_of_items}):
        search_results.append(item)
    
    # Select randomly among items
    
    rand_items = random.sample(search_results, number_of_videos)
    
    # Item identifiers from dictionary object to list of strings
    
    rand_ident = []
    
    for value in rand_items:
        rand_ident.append(value['identifier'])
    
    # Get metadata via get_item() and dig out filenames to match with identifiers
    
    list_of_dict_filenames = []
    
    for value in rand_items:
        dict_filenames = get_item(value['identifier'])
        list_of_dict_filenames.append(dict_filenames.files)
    
    fnames_2dl = []
    
    for m_i in list_of_dict_filenames:
        for file in m_i:
                if file['format'] == 'h.264':
                #    fname = file['name']
                    fnames_2dl.append(file['name'])
                    break
                elif file['format'] == 'MPEG4':
                 #   fname = file['name']
                    fnames_2dl.append(file['name'])
                    break
                elif file['format'] == 'QuickTime':
                  #  fname = file['name']
                    fnames_2dl.append(file['name'])
                    break
                elif file['format'] == '512Kb MPEG4':
                    fnames_2dl.append(file['name'])

    return rand_ident, fnames_2dl