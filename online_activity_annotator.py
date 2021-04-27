# -*- coding: utf-8 -*-

"""
    Online Activity annotator

    This annotator marks up mentions of online activity in clinical texts.
    Online activity is considered to be use of one of the following:
    - the Internet
    - social media
    - online gaming

    Output is in the XML stand-off annotation format that is used
    by the eHOST annotation tool (see https://code.google.com/archive/p/ehost/).

"""

import argparse
import os
import re
import spacy
import sys
import xml.etree.ElementTree as ET

from datetime import datetime
from lexical_annotator import LexicalAnnotatorSequence
from lexical_annotator import LemmaAnnotatorSequence
from token_sequence_annotator import TokenSequenceAnnotator
from detokenizer import Detokenizer
from online_activity_file_sampler_with_cats import remove_unwanted_patterns
from spacy.symbols import LEMMA, LOWER
from xml.dom.minidom import parseString
from xml.parsers.expat import ExpatError

from examples.test_examples import text


class OnlineActivityAnnotator:
    """
    Online Activity Annotator
    
    Annotates mentions of online activity (use of Internet, online gaming or 
    social media) in clinical texts.
    """
    
    def __init__(self, verbose=False):
        """
        Create a new OnlineActivityAnnotator instance.
        
        Arguments:
            - verbose: bool; print all messages.
        """
        print('Online Activity Annotator')
        self.nlp = spacy.load('en_core_web_sm', disable=['ner', 'parser'])
        self.text = None
        self.verbose = verbose
        
        # initialise
        # Load pronoun lemma corrector
        self.load_pronoun_lemma_corrector()
        
        # Load date annotator
        self.load_date_annotator()

        # Load detokenizer
        self.load_detokenizer(os.path.join('..', 'dsh_annotator', 'resources', 'detokenization_rules.txt'))
        self.load_detokenizer(os.path.join('resources', 'detokenization_rules_smig.txt'))

        # Load lexical annotators
        self.load_lexicon('./resources/social_media_lex.txt', LOWER, 'LA')
        self.load_lexicon('./resources/internet_lex.txt', LOWER, 'LA')
        self.load_lexicon('./resources/online_gaming_lex.txt', LOWER, 'LA')
        self.load_lexicon('./resources/health_website_lex.txt', LOWER, 'LA')

        # Load token sequence annotators
        self.load_token_sequence_annotator('level0')

        print('-- Pipeline:', file=sys.stderr)
        print('  -- ' + '\n  -- '.join(self.nlp.pipe_names), file=sys.stderr)

    def load_lexicon(self, path, source_attribute, target_attribute, merge=False):
        """
        Load a lexicon/terminology file for annotation.
        
        Arguments:
            - path: str; the path to the lexicon file.
            - source_attribute: spaCy symbol; the token attribute to match
              on (e.g. LEMMA).
            - target_attribute: spaCy symbol; the token attribute to add the 
              lexical annotations to (e.g. TAG, or custom attribute INTERNET).
            - merge: bool; merge annotated spans into a single span.
        """
        if source_attribute == LEMMA:
            lsa = LemmaAnnotatorSequence(self.nlp, path, target_attribute, merge=merge)
        else:
            lsa = LexicalAnnotatorSequence(self.nlp, path, source_attribute, target_attribute, merge=merge)
        lsa.load_lexicon()
        self.nlp = lsa.add_components()

    def load_pronoun_lemma_corrector(self):
        """
        Load a pipeline component to convert spaCy pronoun lemma (-PRON-) into
        the corresponding word form,
        e.g. ORTH=her LEMMA=-PRON- -> ORTH=her, LEMMA=her.
        """
        component = LemmaCorrector()
        pipe_name = component.name

        if not pipe_name in self.nlp.pipe_names:
            self.nlp.add_pipe(component, last=True)
        else:
            print('-- ', pipe_name, 'exists already. Component not added.')

    def load_date_annotator(self):
        """
        Load a pipeline component to match and annotate certain date 
        expressions.
        """
        component = DateTokenAnnotator()
        pipe_name = component.name

        if not pipe_name in self.nlp.pipe_names:
            self.nlp.add_pipe(component, last=True)
        else:
            print('-- ', pipe_name, 'exists already. Component not added.')

    def load_detokenizer(self, path):
        """
        Load a pipeline component that stores detokenization rules loaded from 
        a file.
        
        Arguments:
            - path: str; the path to the file containing detokenization rules.
        """
        print('-- Detokenizer')
        self.nlp = Detokenizer(self.nlp).load_detokenization_rules(path, verbose=self.verbose)

    def load_token_sequence_annotator(self, name):
        """
        Load a token sequence annotator pipeline component.
        TODO allow for multiple annotators, cf. lemma and lexical annotators.
        TODO add path argument to specify rule file.
        
        Arguments:
            - name: str; the name of the token sequence annotator - this 
                    *must* be the name (without the .py extension) of the file
                    containing the token sequence rules.
        """
        tsa = TokenSequenceAnnotator(self.nlp, name, verbose=self.verbose)
        if tsa.name not in self.nlp.pipe_names:
            self.nlp.add_pipe(tsa)

    def get_text(self):
        """
        Return the text of the current annotator instance.
        
        Return:
            - text: str; the text of the document being processed.
        """
        return self.text

    def annotate_text(self, text):
        """
        Annotate a text string.
        
        Arguments:
            - text: str; the text to annotate.
        
        Return:
            - doc: spaCy Doc; the annotated Doc object.
        """
        self.text = text
        return self.nlp(text)

    def annotate_file(self, path, clean_text):
        """
        Annotate the contents of a text file.
        
        Arguments:
            - path: str; the path to a text file to annotate.
        
        Return:
            - doc: spacy Doc; the annotated Doc object.
        """
        # TODO check for file in input
        # TODO check encoding
        f = open(path, 'r', encoding='Latin-1')
        self.text = f.read()
        self.text = remove_unwanted_patterns(self.text, verbose=False)
        
        if len(self.text) >= 1000000:
            print('-- Unable to process very long text text:', path)
            return None
        
        doc = self.nlp(self.text)
        
        return doc
    
    def merge_spans(self, doc):
        """
        Merge all longest matching DSH token sequences into single spans.
        
        Arguments:
            - doc: spaCy Doc; the current Doc object.
        
        Return:
            - doc: spaCy Doc; the current Doc object with merged longest spans.
        """
        offsets = []
        i = 0
        while i < len(doc):
            token = doc[i]
            if token._.MENTION:
                mtype = token._.MENTION
                start = i
                while token._.MENTION == mtype:
                    mtype = token._.MENTION
                    i += 1
                    if i == len(doc):
                        print('-- Warning: index is equal to document length:', i, token, len(doc), file=sys.stderr)
                        break
                    token = doc[i]
                end = i
                offsets.append((start, end))
            i += 1
        
        with doc.retokenize() as retokenizer:
            for (start, end) in offsets:
                #print('Merging tokens:', start, end, doc[start:end], file=sys.stderr)
                attrs = {'LEMMA': ' '.join([token.lemma_ for token in doc[start:end]]).replace('# ', '#')}
                retokenizer.merge(doc[start:end], attrs=attrs)

        return doc

    def print_spans(self, doc):
        """
        Output all spans in CoNLL-style token annotations to stdout

        Arguments:
            - doc: spaCy Doc; the current Doc object
        """
        s = '\n'
        s += 'PIPELINE:\n-- ' + '\n-- '.join(self.nlp.pipe_names)
        s += '\n\n'
        s += '{:<10}{:<10}{:<10}{:<10}{:<10}{:<10}{:<10}{:<10}'.format('INDEX', 'WORD', 'LEMMA', 'LOWER', 'POS1', 'POS2', 'HEAD', 'DEP')

        cext = set()        
        for a in doc.user_data:
            cext.add(a[1])

        cext = sorted(cext)

        for a in cext:
            s += '{:<10}'.format(a)

        s += '\n'

        s += '{:<10}{:<10}{:<10}{:<10}{:<10}{:<10}{:<10}{:<10}'.format('-----', '----', '-----', '----', '----', '----', '----', '----')

        for a in cext:
            s += '{:<10}'.format('-' * len(a))

        print(s, file=sys.stderr)
        
        for token in doc:
            s = '{:<10}{:<10}{:<10}{:<10}{:<10}{:<10}{:<10}{:<10}'.format(token.i, token.text, token.lemma_, token.lower_, token.tag_, token.pos_, token.head.i, token.dep_)
            for a in cext:
                val = token._.get(a)
                s += '{:10}'.format(val or '_')
            print(s, file=sys.stderr)

    def build_ehost_output(self, doc):
        """
        Construct a dictionary representation of all annotations.

        Arguments:
            - doc: spacy Doc; the processed spaCy Doc object.
        
        Return:
            - mentions: dict; a dictionary containing all annotations ready for
                        output in eHOST XML format.
        """
        mentions = {}
        n = 1
        for token in doc:
            if token._.MENTION:
                mention_id = 'EHOST_Instance_' + str(n)
                annotator = 'SYSTEM'
                mclass = token._.MENTION
                comment = None
                start = token.idx
                end = token.idx + len(token.text)
                text = token.text
                n += 1
                mentions[mention_id] = {'annotator': annotator,
                                        'class': mclass,
                                        'comment': comment,
                                        'end': str(end),
                                        'start': str(start),
                                        'text': text
                                        }

        return mentions
    
    def write_ehost_output(self, pin, annotations, verbose=False):
        """
        Write an annotated eHOST XML file to disk.
        
        Arguments:
            - pin: str; the input file path (must be in eHOST directory structure).
            - annotations: dict; the dictionary of detected annotations.
            - verbose: bool; print all messages.
        
        Return:
            - root: Element; the root node of the new XML ElementTree object.
        """
        ehost_pout = os.path.splitext(pin.replace('corpus', 'saved'))[0] + '.txt.knowtator.xml'

        root = ET.Element('annotations')
        root.attrib['textSource'] = os.path.basename(os.path.splitext(pin.replace('.knowtator.xml', ''))[0] + '.txt')

        n = 1
        m = 1000
        for annotation_id in sorted(annotations.keys()):
            annotation = annotations[annotation_id]

            annotation_node = ET.SubElement(root, 'annotation')
            mention = ET.SubElement(annotation_node, 'mention')
            mention_id = 'EHOST_Instance_' + str(n)
            mention.attrib['id'] = mention_id
            annotator = ET.SubElement(annotation_node, 'annotator')
            annotator.attrib['id'] = 'eHOST_2010'
            annotator.text = annotation['annotator']
            spanned_text = ET.SubElement(annotation_node, 'spannedText')

            if annotation.get('comment', None) is not None:
                comment = ET.SubElement(annotation_node, 'annotationComment')
                comment.text = annotation['comment']

            creation_date = ET.SubElement(annotation_node, 'creationDate')
            creation_date.text = datetime.now().strftime('%a %b %d %H:%M:%S %Z%Y')

            span = ET.SubElement(annotation_node, 'span')
            span.attrib['start'] = annotation['start']
            span.attrib['end'] = annotation['end']

            spanned_text.text = annotation['text']

            class_mention = ET.SubElement(root, 'classMention')
            class_mention.attrib['id'] = mention_id
            mention_class_node = ET.SubElement(class_mention, 'mentionClass')
            mention_class_node.attrib['id'] = annotation['class']
            mention_class_node.text = annotation['text']
            
            n += 1
            m += 1

        # Create Adjudication status with default values
        adj_status = ET.SubElement(root, 'eHOST_Adjudication_Status')
        adj_status.attrib['version'] = '1.0'
        adj_sa = ET.SubElement(adj_status, 'Adjudication_Selected_Annotators')
        adj_sa.attrib['version'] = '1.0'
        adj_sc = ET.SubElement(adj_status, 'Adjudication_Selected_Classes')
        adj_sc.attrib['version'] = '1.0'
        adj_o = ET.SubElement(adj_status, 'Adjudication_Others')
        check_s = ET.SubElement(adj_o, 'CHECK_OVERLAPPED_SPANS')
        check_s.text = 'false'
        check_a = ET.SubElement(adj_o, 'CHECK_ATTRIBUTES')
        check_a.text = 'false'
        check_r = ET.SubElement(adj_o, 'CHECK_RELATIONSHIP')
        check_r.text = 'false'
        check_cl = ET.SubElement(adj_o, 'CHECK_CLASS')
        check_cl.text = 'false'
        check_co = ET.SubElement(adj_o, 'CHECK_COMMENT')
        check_co.text = 'false'

        # Print to screen
        xmlstr = ET.tostring(root, encoding='utf8', method='xml')
        try:
            pxmlstr = parseString(xmlstr)
        except ExpatError as e:
            with open('T:/Andre Bittar/Projects/RS_Internet/batch_err.log', 'a+') as b_err:
                print('Unable to create XML file:', ehost_pout, str(e), file=b_err)
            b_err.close()
            return root

        if verbose:
            print(pxmlstr.toprettyxml(indent='\t'), file=sys.stderr)

        # Write to file
        #tree = ET.ElementTree(root)
        #tree.write(ehost_pout, encoding="utf-8", xml_declaration=True)
        open(ehost_pout, 'w').write(pxmlstr.toprettyxml(indent='\t'))
        if verbose:
            print('-- Wrote EHOST file: ' + ehost_pout, file=sys.stderr)

        return root

    def process(self, path, clean_text=True, write_output=True):
        """
        Process a single document or directory structure.
        
        Arguments:
            - path: str; indicates text file or directory to process. If a directory, the
                structure must be that used by the eHOST annotation tool.
            - clean_text: bool; clean text prior to processing by removing unwanted patterns.
            - write_output: bool; save the annotated output to file.
        
        Return:
            - global_mentions: dict; a dictionary containing all annotated mentions.
        """
        global_mentions = {}

        if os.path.isdir(path):
            print('-- Processing directory...', file=sys.stderr)
            files = os.listdir(path)
            
            for f in files:
                pin = os.path.join(path, f)
                if self.verbose:
                    print('-- Processing file:', pin, file=sys.stderr)
                # Annotate and print results
                doc = self.annotate_file(pin, clean_text)
                doc = self.merge_spans(doc)
                
                if self.verbose:
                    self.print_spans(doc)
                
                mentions = self.build_ehost_output(doc)
                global_mentions[f + '.knowtator.xml'] = mentions
                                
                if write_output:
                    self.write_ehost_output(pin, mentions, verbose=self.verbose)
                
        elif os.path.isfile(path):
            print('-- Processing file:', path, file=sys.stderr)
            doc = self.annotate_file(path, clean_text)
            doc = self.merge_spans(doc)
            
            if self.verbose:
                self.print_spans(doc)
            
            mentions = self.build_ehost_output(doc)
            key = os.path.basename(path)
            global_mentions[key] = mentions

            if write_output:
                self.write_ehost_output(path, mentions, verbose=self.verbose)

        else:
            print('-- Processing text string:', path, file=sys.stderr)
            path = remove_unwanted_patterns(path, verbose=False)
            doc = self.nlp(path)
            doc = self.merge_spans(doc)

            if self.verbose:
                self.print_spans(doc)

            mentions = self.build_ehost_output(doc)
            key = os.path.basename(path)
            global_mentions[key] = mentions

            if write_output:
                self.write_ehost_output('test.txt', mentions, verbose=self.verbose)
        
        return global_mentions

    def process_text(self, text, text_id, clean_text=False, write_output=False, verbose=False):
        """
        Process a text string.
        
        Arguments:
            - text: str; the input text.
            - text_id: str; a user-defined identifier for the text.
            - clean_text: bool; clean text prior to processing by removing unwanted patterns.
            - verbose: bool; print all messages.

        Return:
            - global_mentions: dict; a dictionary containing all annotated mentions.
        """
        self.verbose = verbose
        if self.verbose:
            print('-- Processing text string:', text, file=sys.stderr)
        
        global_mentions = {}
        if clean_text:
            text = remove_unwanted_patterns(text, verbose=verbose)
        doc = self.nlp(text)
        doc = self.merge_spans(doc)
        
        if self.verbose:
            self.print_spans(doc)

        mentions = self.build_ehost_output(doc)
        
        global_mentions[text_id] = mentions

        if write_output:
            self.write_ehost_output('test.txt', mentions, verbose=self.verbose)
        
        return global_mentions


class LemmaCorrector(object):
    """
    Lemma Corrector
    
    Replace spaCy's default lemma for relevant pronouns and other words.
    """
    
    def __init__(self):
        """
        Create a new LemmaCorrector instance.
        """
        self.name = 'pronoun_lemma_corrector'

    def __call__(self, doc):
        for token in doc:
            if token.lower_ in ['she', 'her', 'herself', 'themselves']:
                token.lemma_ = token.lower_
            if token.lower_ == 'overdoses':
                token.lemma_ = 'overdose'
        return doc


class DateTokenAnnotator(object):
    """
    Date Token Annotator
    
    Annotate specific and easily matched date patterns.
    """

    def __init__(self):
        """
        Create a new DateTokenAnnotator instance.
        """
        self.name = 'date_token_annotator'

    def __call__(self, doc):
        # Date pattern regexes
        yyyy = '(19[0-9][0-9]|20[0-9])'
        ddmmyy = '(0?[1-9]|[12][0-9]|3[01])\/(0[1-9]|1[012])\/([0-9][0-9])'
        ddmmyyyy = '(0?[1-9]|[12][0-9]|3[01])\/(0[1-9]|1[012])\/(19[0-9][0-9]|20[0-9])'
        ddmmyy_dot = '(0?[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[012])\.([0-9][0-9])'
        ddmmyyyy_dot = '(0?[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[012])\.(19[0-9][0-9]|20[0-9])'
        date = '(' + yyyy + '|' + ddmmyy + '|' + ddmmyyyy + '|' + ddmmyy_dot + '|' + ddmmyyyy_dot + ')'
        for token in doc:
            if re.search(date, token.lemma_) is not None:
                token._.TIME = 'TIME'
        return doc


def test(smiga):
    main_dir = 'T:/Andre Bittar/Projects/RS_Internet/NEW_2'
    pdirs = os.listdir(main_dir)
    for pdir in pdirs:
        pin = os.path.join(main_dir, pdir, 'corpus').replace('\\', '/')
        if os.path.isdir(pin):
            print(pin)
            smiga.process(pin, write_output=False)    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Online Activity Annotator')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--input_dir', type=str, nargs=1, help='the path to the directory containing text files to process.', required=False)
    group.add_argument('-f', '--input_file', type=str, nargs=1, help='the path to a text file to process.', required=False)
    group.add_argument('-t', '--text', type=str, nargs=1, help='a text string to process.', required=False)
    group.add_argument('-e', '--examples', action='store_true', help='run on test examples (no output to file).', required=False)
    parser.add_argument('-w', '--write_output', action='store_true', help='write output to file.', required=False)
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode.', required=False)
    
    if len(sys.argv) <= 1:
        parser.print_help()
        sys.exit(0)
    
    args = parser.parse_args()

    oaa = OnlineActivityAnnotator(verbose=args.verbose)
    
    if args.text is not None:
        oa_annotations = oaa.process_text(args.text[0], 'text_001', write_output=args.write_output, verbose=args.verbose)
    elif args.input_dir is not None:
        if os.path.isdir(args.input_dir[0]):
            oa_annotations = oaa.process(args.input_dir[0], write_output=args.write_output)
        else:
            print('-- Error: argument -d/--input_dir must be an existing directory.\n')
            parser.print_help()
    elif args.input_file is not None:
        if os.path.isfile(args.input_file[0]):
            oa_annotations = oaa.process(args.input_file[0], write_output=args.write_output)
        else:
            print('-- Error: argument -f/--input_file must be an existing text file.\n')
            parser.print_help()
    elif args.examples:
        print('-- Running examples...', file=sys.stderr)
        oa_annotations = oaa.process_text(text, 'text_001', write_output=False, verbose=True)
