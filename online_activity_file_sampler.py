# -*- coding: utf-8 -*-
"""
    Online Activity file sampler script

    This script searches for files containing certain keywords that pertain to
    use of online activity - social media, Internet and online gaming.

"""

import os
import re
from ehost_annotation_reader import get_corpus_files
from shutil import copy


"""d1 = 'T:/Sophie Epstein/Annotations/annotation_folders'
d2 = 'T:/Sophie Epstein/Annotations/blind_test_data/blind_testdata_annotation'
d3 = 'T:/Sophie Epstein/Annotations/blind_test_data2/blind_testdata_annotation'

files = get_corpus_files(d1, file_types='txt') + \
        get_corpus_files(d2, file_types='txt') + \
        get_corpus_files(d3, file_types='txt')
"""

regex_1 = '(on[ \-]line|internet|askfm|bebo|blog|face.{0,2}book|fb|google\+' + \
        'you.{0,2}tube|tumblr|twitter|tweet|flickr|pinterest|vimeo|periscope|' + \
        'insta.{0,2}gram|hashtag|linkedin|snap.{0,2}chat|forum|reddit|pinterest' + \
        'social (media|network.*)|skype|tinder|web.{0,2}site)|wechat|wordpress|' + \
        'whats.{0,2}app|twitch|video sharing|instant messag.+|image sharing|' + \
        'e-communi.+|vine|myspace|website|chatroom|gaming|videos|recovery account|' + \
        'spam account|4chan|lolcow|dark web|deep web'

regex_2 = '\W(4chan|Android|askFM|Bebo|Blackberry|Blog|Call of duty|Chatroom|' + \
        'Club penguin|Computer|Coraline|Counter-strike|Counter strike|Dark web|' + \
        'Deep Web|Dota 2|Dragon age|e-communi.*|Face book|Facebook|Fallout|FB|' + \
        'Flickr|Forum[a-z]*|Gaming|Ghostbusters|Google|Grand Theft Auto|HALO|' + \
        'Hashtag[a-z]*|Image Sharing|Instagram|Instant messag[a-z]*|iPhone|' + \
        'League of legends|Linkedin|lolcow|Minecraft|Miniclip|Myspace|' + \
        'PC|Periscope|Pinterest|Playstation|Recovery account|Reddit|' + \
        'Sims|Smartphone|Smite|Snapchat|Social Media|Social Network[a-z]*|' + \
        'Spam Account|Tumblr|Tweet[a-z]*|Twitter|Video game|Video sharing|Vimeo|' + \
        'Vine|web address|Wordpress|World of tanks|World of warcraft|X-men|Xbox|' + \
        'youtube)\W'

hashtag_regex = '#[a-z][a-z0-9]+'
pc_regex = ' PC[ \.,]'
internet_regex  = 'Internet (?!threat)'
online_regex = 'online(?!( +security| *\"))'
website_regex = 'websites?'

regex = regex_2 + '|' + hashtag_regex + '|' + pc_regex + '|' + internet_regex + '|' + online_regex  + '|' + website_regex

DDIR = 'T:/Rosie Sedgwick/SE_Suicidality/ALL_3'

def remove_unwanted_patterns(text):
    """
    Removes certain unwanted patterns that are likely to create noise.
    
    Arguments:
        - text: str; the text to search and modify.
    
    Return:
        - text: str; the modified text.
    """
    text = re.sub('Website *:', '', text, flags=re.I)
    text = re.sub('DISCLAIMER.+-----------------------.+\n', '', text)
    return text

def copy_files_to_sample(files, copy_schema=None):
    """
    Create a corpus of files to sample from.
    
    Arguments:
        - files: list; a list of files.
        - copy_schema: bool; copy the eHOST configuration file.
    """
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

def process():
    """
    Run the whole search process.
    
    Return:
        - files_to_sample: list; the files to sample from.
    """
    main_src_dir = 'T:/Andre Bittar/Corpora/SE_Suicidality/annotations/'
    files = get_corpus_files(main_src_dir, file_types='txt')
    files_to_sample = []

    if not os.path.isdir(DDIR):
        os.makedirs(DDIR)

    report_out = open(DDIR + '/sampled_files.txt', 'w')

    for f in files:
        text = open(f, 'r', encoding='latin-1').read()

        # remove difficult patterns to exclude
        text = remove_unwanted_patterns(text)

        # now do matching
        match = re.search(regex, text, flags=re.I)
        if match is not None:
            print(f + '\t' + match.group(0))
            print(f + '\t' + match.group(0), file=report_out)
            files_to_sample.append(f)

    print()
    print(len(files_to_sample))

    return files_to_sample

#files_to_sample = process()
#copy_files_to_sample(files_to_sample, copy_schema='T:/Rosie Sedgwick/SE_Suicidality/config/projectschema.xml')