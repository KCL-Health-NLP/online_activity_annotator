# -*- coding: utf-8 -*-
"""
Created on Wed Dec 12 10:51:31 2018

@author: ABittar
"""

import os
import pickle
import re
import sys

sys.path.insert(0, 'T:/Andre Bittar/workspace/utils')

from ehost_annotation_reader import get_corpus_files
from shutil import copy

"""d1 = 'T:/Sophie Epstein/Annotations/annotation_folders'
d2 = 'T:/Sophie Epstein/Annotations/blind_test_data/blind_testdata_annotation'
d3 = 'T:/Sophie Epstein/Annotations/blind_test_data2/blind_testdata_annotation'

files = get_corpus_files(d1, file_types='txt') + \
        get_corpus_files(d2, file_types='txt') + \
        get_corpus_files(d3, file_types='txt')
"""

re_hashtag = r' #[a-z][a-z0-9]+'

re_social_media = re_hashtag + r'|4[\- ]?chan|askFM|Bebo|Blog[^ ]*|(chat|talk)[^ ]*\ +on[\- ]*line|Chatroom[^ ]*|' + \
                  r'communicat[^ ]*\ +on[\- ]*line|e\-communi[^ ]*|e[\- ]?communi[^ ]*|Face[\- ]*book|' + \
                  r'FB|Flickr|Forum[^ ]*|Hashtag[^ ]*|Image\ +Sharing|' + \
                  r'Insta[\- ]?gram|Instant[\- ]+messag[^ ]*|Linked\-?in|lol\-?cow|lol\-?cow\.farm|' + \
                  r'My\-?space|Periscope|Recovery account|Reddit|' + \
                  r'Snap\-?chat|Social[\- ]+Media|Social[\- ]+Network[^ ]*|Spam\ +Account|' + \
                  r'Tumblr|Tweet[^ ]*|Twitter|' + \
                  r'Video\ +shar[^ ]*|Vimeo|Vine|Word[\- ]?press|you[\- ]?tube[^ ]*'

re_internet_word = r'Internet (?!threat)'
re_online = r'on[\- ]*line(?!( +security| *\"))'

# removed: Link(?!ed)
re_internet = re_internet_word + r'|' + re_online + r'|Android|Black[\- ]*berry|' +  \
              r'Computer|(Dark|Deep)[\- ]*Web|' + \
              r'[^@]Googl[^ \.]*|i\-?phone|Lap\-?top|Mac|Mac\-?book|' + \
              r'Smart[\- ]*phone|web[\- ]*address|web[\- ]*site[^ ]*|Pint?erest'

re_online_gaming = r'Call of Duty|Club Penguin|Coraline|Counter[\- ]*strike|Dota 2|' + \
                   r'Dragon age|Fall\-?out|gam[^ ]* on[\- ]*line|Game[\- ]*Boy|Gaming|' + \
                   r'Ghostbusters|Grand Theft Auto|HALO|League of legends|' + \
                   r'Mine[\- ]*craft|Mini[\- ]*clip|Nintendo|on[\- ]*line Gam[^ ]*|PC gam[^ ]*|' + \
                   r'Play[\- ]*station|Simm?s|Smite|video gam[^ ]*|video\-gam[^ ]*|web gam[^ ]*|' + \
                   r'web\-?gam[^ ]*|Wii|World of tanks|World of warcraft|X\-?box|X\-?men'

REGEX = r'\b(' + re_social_media + r'|' + re_internet + r'|' + re_online_gaming + r')\b'

DDIR = 'T:/Andre Bittar/Projects/RS_Internet/NEW_2'


def remove_unwanted_patterns(text, verbose=False):
    len_b = len(text)
    patterns = {'Website[\t ]*[:\-]': re.I + re.M + re.DOTALL,
                'Visit our[\t ]*website[\t ]+(http://)?www.slam.nhs.uk': re.I + re.M + re.DOTALL,
                'Sent from my iPhone': re.I,
                'DISCLAIMER.+': re.M + re.DOTALL,
                'This email and any files.+?visit http://www.messagelabs.com/email': re.M + re.DOTALL,
                'Web[^\n\r\.\;\,\:]+?[\n\r\t\s]+www.dawba.net': re.M + re.DOTALL,
                '\*\*\*\*\*\*\*\*\*\*.+\*\*\*\*\*\*\*\*\*\*': re.M + re.DOTALL}
    
    # remove difficult patterns to exclude - replace with equal number of spaces
    for p in patterns:
        flags = patterns.get(p)
        matches = re.findall(p, text, flags=flags)
        if matches is not None:
            for m in matches:
                if verbose:
                    print('-- Ignoring text:', '>' + m + '<')
                text = re.sub(re.escape(m), ' ' * len(m), text, flags=flags)
    
    len_a = len(text)
    
    # ensure text stays same length after replacements
    assert len_b == len_a
    
    return text


def get_initial_files(reload=True):
    """
    Do this first so we don't have to repeat it every time we run the script.
    """
    if reload:
        main_src_dir = 'T:/Andre Bittar/Corpora/SE_Suicidality/annotations/'
        files = get_corpus_files(main_src_dir, file_types='txt')
    else:
        files = pickle.load(open('T:/Andre Bittar/Projects/RS_Internet/initial_files.txt', 'rb'))

    return files


def copy_files_to_sample(files, copy_schema=None):
    print('-- Copying sampled files to main directory...', end='')
    for src in files:
        dest = src.replace('T:/Andre Bittar/Corpora/SE_Suicidality/annotations', DDIR)
        ddest = re.sub('(corpus).+', '\g<1>', dest)
        sdest = re.sub('corpus', 'saved', ddest)
        cdest = re.sub('corpus', 'config', ddest)
        if not os.path.exists(ddest):
            os.makedirs(ddest)
            os.makedirs(sdest)
            os.makedirs(cdest)
        if copy_schema is not None:
            if os.path.isfile(copy_schema):
                print('-- Copying schema to', cdest)
                copy(copy_schema, cdest)
            else:
                print('-- Warning, invalid project schema:', copy_schema)
        print('-- Copying file', src, dest)
        copy(src, dest)
    print('Done.')


def process(files, verbose=False):
    files_to_sample = []

    if not os.path.isdir(DDIR):
        print('-- Created new project directory:', DDIR)
        os.makedirs(DDIR)

    report_out = open(DDIR + '/sampled_files.txt', 'w', encoding='latin-1')

    for f in files:
        text = open(f, 'r', encoding='latin-1').read()

        # remove difficult patterns to exclude
        text = remove_unwanted_patterns(text)

        # now do matching
        match = re.search(REGEX, text, flags=re.I)
        if match is not None:
            start, end = match.span()
            tstart = start - 50
            tend = end + 50
            if verbose:
                print(f + '\t>' + match.group(0) + '<', '(' + str(start) + ', ' + str(end) + ')')
                print(text[tstart:start] + '\t>' + text[start:end] + '<\t' + text[end:tend])
            print(f + '\t>' + match.group(0) + '<', '(' + str(start) + ', ' + str(end) + ')', file=report_out)            
            files_to_sample.append(f)

    print()
    print(len(files_to_sample))

    return files_to_sample


if __name__ == '__main__':
    if False:
        reload = False
        files = get_initial_files(reload=reload)
        if reload:
            pickle.dump(files, open('T:/Andre Bittar/Projects/RS_Internet/initial_files.txt', 'wb'))
        files_to_sample = process(files)
        copy_files_to_sample(files_to_sample, copy_schema='T:/Rosie Sedgwick/SE_Suicidality/config/projectschema.xml')