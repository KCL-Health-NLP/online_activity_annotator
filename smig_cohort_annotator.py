# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 11:18:29 2019

@author: ABittar
"""

import datetime
import os
import pandas as pd
import sys

sys.path.append('T:/Andre Bittar/workspace/utils')

from smig_annotator import SMIGAnnotator
from ehost_annotation_reader import convert_file_annotations, get_corpus_files, load_mentions_with_attributes
from pandas import Timestamp
from pprint import pprint
from sklearn.metrics import cohen_kappa_score, precision_recall_fscore_support
from time import time


def has_SMIG_mention(mentions):
    mentions = convert_file_annotations(mentions)
    for mention in mentions:
        mclass = mention.get('class', None)
        print(mclass)
        
        if mclass is not None:
            return True
                    
    return False


def test():
    smiga = SMIGAnnotator()
    
    texts = ['She is always playing on the computer.', 'He play Warcraft online.', 'He spends too much tim eon Facebook.']
    
    n = 1
    global_mentions = {}
    
    for text in texts:
        text_id = 'text_' + str(n).zfill(5)
        n += 1
        mentions = smiga.process_text(text, text_id, verbose=True, write_output=False)
        print('HAS SMIG:', has_SMIG_mention(mentions))
        global_mentions.update(mentions)
    
    pprint(global_mentions)



def count_flagged_patients(df_processed, key):
    """
    key: dsh_YYYYMMDD_tmp or dsh_YYYYMMDD_notmp
    """
    n = 0
    t = 0
    for g in df_processed.groupby('brcid'):
        for i, row in g[1].iterrows():
            if row[key] == True:
                n += 1
                break
        t += 1
    
    print('Flagged patients:', n)
    print('Total patients  :', t)
    print('% flagged       :', n / t * 100)


def evaluate_sys(results, sys_results):
    """
    
    """
    x_gold = []
    x_sys = []
    
    for brcid in results:
        x_gold.append(results.get(brcid) > 0)
        x_sys.append(sys_results.get(brcid) > 0)
 
    n = len(x_gold)
    n_gold = len([x for x in x_gold if x == True])
    n_sys = len([x for x in x_sys if x == True])
    
    report_string = 'Patient-level performance metrics\n'
    report_string += '---------------------------------\n'
    report_string += 'Gold patients:' + str(n_gold) + ' (' + str(n_gold / n * 100) + '%)\n'
    report_string += 'Sys patients :' + str(n_sys) + ' (' + str(n_sys / n * 100) + '%)\n'
    scores = {}
    scores['macro'] = precision_recall_fscore_support(x_gold, x_sys, average='macro')
    scores['micro'] = precision_recall_fscore_support(x_gold, x_sys, average='micro')
            
    for score in scores:
        report_string += 'precision (' + score + '): ' + str(scores[score][0]) + '\n'
        report_string += 'recall    (' + score + '): ' + str(scores[score][1]) + '\n'
        report_string += 'f-score   (' + score + '): ' + str(scores[score][2]) + '\n'

    k = cohen_kappa_score(x_gold, x_sys)
    report_string += 'kappa            : ' + str(k) + '\n'

    print(report_string)


def batch_process(main_dir):
    """
    Runs on actual files and outputs new XML.
    """
    ga = SMIGAnnotator(verbose=False)
    
    #main_dir = 'Z:/Andre Bittar/Projects/KA_Self-harm/data/text'
    
    pdirs = os.listdir(main_dir)
    n = len(pdirs)
    i = 1
    
    t0 = time()
    
    for pdir in pdirs:
         pin = os.path.join(main_dir, pdir, 'corpus').replace('\\', '/')
         _ = smiga.process(pin, write_output=True)
         print(i, '/', n, pin)
         i += 1

    t1 = time()
    
    print(t1 - t0)


def process(pin):
    """
    Runs on a DataFrame that contains the text for each file.
    Outputs True for documents with relevant mention.
    Does not write new XML.
    All saved to the DataFrame.
    """
    
    now = datetime.datetime.now().strftime('%Y%m%d')
    
    smiga = SMIGAnnotator(verbose=False)
    df = pd.read_pickle(pin)
    df['dsh'] = False
    n = len(df)
    
    t0 = time()
    for i, row in df.iterrows():
        docid = row.cn_doc_id
        text = row.text_content
        mentions = smiga.process_text(text, docid, write_output=False)
        df.at[i, 'smig_' + now] = has_SMIG_mention(mentions)
        if i % 1000 == 0:
            print(i, '/', n)
        
    t1 = time()
    
    print(t1 - t0)
    
    print('-- Wrote file:', pin)
    df.to_pickle(pin)
    
    return df


if __name__ == '__main__':
    print('-- Run one of the two functions...', file=sys.stderr)
    #test()
    #df_processed = process('Z:/Andre Bittar/Projects/KA_Self-harm/data/all_text.pickle', check_temporality=True)
    #batch_process('T:/Andre Bittar/Projects/KA_Self-harm/Adjudication/system_train_dev_patient/files')
    