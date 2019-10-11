from spacy.tokens import Token

#################################
# Custom attribute declarations #
#################################

Token.set_extension('MENTION', default=False, force=True)
Token.set_extension('TIME', default=False, force=True) # this shouldn't be here but it is called in the main class for dates

#################################
# Token sequence rules, Level 0 #
#################################

RULES = [
    # SOCIAL MEDIA
    {
        # chat online
        'name': 'CHAT_ONLINE',
        'pattern': [{'LEMMA': {'REGEX': '(chat|communicat|talk).*'}}, {'LEMMA': {'IN': ['online', 'on-line']}}],
        'avm': {'ALL': {'MENTION': 'SOCIAL_MEDIA'}},
        'merge': False
     },
     {
        # chat on line
        'name': 'CHAT_ON_LINE',
        'pattern': [{'LEMMA': {'REGEX': '(chat|communicat|talk).*'}}, {'LEMMA': 'on'}, {'LOWER': 'line'}],
        'avm': {'ALL': {'MENTION': 'SOCIAL_MEDIA'}},
        'merge': False
     },
     {
        # e-communication
        'name': 'E-COMMUNCATE',
        'pattern': [{'LEMMA': {'REGEX': '^e-?(communicat).*'}}],
        'avm': {'ALL': {'MENTION': 'SOCIAL_MEDIA'}},
        'merge': False
     },
     {
        # instant messaging
        'name': 'IM',
        'pattern': [{'LEMMA': {'REGEX': 'instant.*'}}, {'LEMMA': {'IN': ['message', 'messaging']}}],
        'avm': {'ALL': {'MENTION': 'SOCIAL_MEDIA'}},
        'merge': False
     },
     {
        # video sharing
        'name': 'VIDEO_SHARING',
        'pattern': [{'LEMMA': 'video'}, {'LEMMA': {'IN': ['share', 'sharing']}}],
        'avm': {'ALL': {'MENTION': 'SOCIAL_MEDIA'}},
        'merge': False
     },
     {
        # #hashtag
        'name': 'HASHTAG',
        'pattern': [{'ORTH': {'REGEX': '^#[A-Za-z]+[^ ]+$'}}],
        'avm': {'ALL': {'MENTION': 'SOCIAL_MEDIA'}},
        'merge': False
     },
     {
        # SOCIAL_MEDIA (lexical annotation)
        'name': 'CHAT_ON_LINE',
        'pattern': [{'_': {'LA': 'SOCIAL_MEDIA'}}],
        'avm': {'ALL': {'MENTION': 'SOCIAL_MEDIA'}},
        'merge': False
     },
     {
        # face book
        'name': 'SOCIAL_MEDIA_SEQUENCE',
        'pattern': [{'_': {'LA': 'SOCIAL_MEDIA'}, 'OP': '+'}],
        'avm': {'ALL': {'MENTION': 'SOCIAL_MEDIA'}},
        'merge': False
     },
     {
        # Twitter:  @NHSGreenwichCCG
        'name': 'TWITTER_HANDLE',
        'pattern': [{'LOWER': 'twitter'}, {'POS': 'PUNCT', 'OP': '+'}, {'POS': 'SPACE', 'OP': '*'}, {'ORTH': {'REGEX': '(?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+)'}}],
        'avm': {'ALL': {'MENTION': False}},
        'merge': False
     },
     # ONLINE GAMING
     {
        # online gaming
        'name': 'ONLINE_GAMING',
        'pattern': [{'LEMMA': {'IN': ['online', 'on-line']}}, {'LEMMA': {'IN': ['game', 'gamer', 'gaming']}}],
        'avm': {'ALL': {'MENTION': 'ONLINE_GAMING', 'LA': 'GAMING'}},
        'merge': False
     },
     {
        # pc game
        'name': 'PC_GAMING',
        'pattern': [{'LEMMA': {'IN': ['pc', 'computer', 'video']}}, {'LEMMA': {'IN': ['game', 'gamer', 'gaming']}}],
        'avm': {'ALL': {'MENTION': 'ONLINE_GAMING', 'LA': 'GAMING'}},
        'merge': False
     },
     {
        # playing fortnight
        'name': 'PLAY_FORTNIGHT',
        'pattern': [{'LEMMA': {'IN': ['play', 'playing']}}, {'LOWER': 'fortnight'}],
        'avm': {'ALL': {'MENTION': 'ONLINE_GAMING'}},
        'merge': False
     },
     {
        # mine craft
        'name': 'GAMING_SEQUENCE',
        'pattern': [{'_': {'LA': 'GAMING'}, 'OP': '+'}],
        'avm': {'ALL': {'MENTION': 'ONLINE_GAMING'}},
        'merge': False
     }, 
     # INTERNET
     {
        # surf the web
        'name': 'SURF_THE_WEB',
        'pattern': [{'LEMMA': {'IN': ['browse', 'navigate', 'surf', 'browsing', 'navigating', 'surfing']}}, {'LEMMA': 'the'}, {'LOWER': {'IN': ['internet', 'inter-net', 'web']}}],
        'avm': {'ALL': {'MENTION': 'INTERNET'}},
        'merge': False
     },
     {
        # Website: www.samaritans.org.uk
        'name': 'WEB_HEALTH_WEB',
        'pattern': [{'LOWER': 'website'}, {'POS': 'SPACE', 'OP': '*'}, {'POS': 'PUNCT'}, {'POS': 'SPACE', 'OP': '*'}, {'_': {'LA': 'HEALTH_WEB'}}],
        'avm': {'ALL': {'MENTION': 'INTERNET'}},
        'merge': False
     },
     {
        # you tube
        'name': 'INTERNET_SEQUENCE',
        'pattern': [{'_': {'LA': 'INTERNET'}, 'OP': '+'}],
        'avm': {'ALL': {'MENTION': 'INTERNET'}},
        'merge': False
     },
     {
        # on his/her tablet
        'name': 'ON_DET_TABLET',
        'pattern': [{'LOWER': 'on'}, {'LOWER': {'IN': ['his', 'her']}, 'OP': '?'}, {'LOWER': 'tablet'}],
        'avm': {'ALL': {'MENTION': 'INTERNET'}},
        'merge': False
     },
     {
        # his/her tablet
        'name': 'DET_TABLET',
        'pattern': [{'LOWER': {'IN': ['a', 'the', 'his', 'her']}}, {'LOWER': 'tablet'}],
        'avm': {'ALL': {'MENTION': 'INTERNET'}},
        'merge': False
     },
     {
        # his/her mum's tablet
        'name': 'DET_POS_TABLET',
        'pattern': [{'LOWER': {'IN': ['his', 'her', 'their']}}, {'LOWER': {'IN': ['dad', 'mum', 'brother', 'sister']}}, {'LOWER': "'s"}, {'LOWER': 'tablet'}],
        'avm': {'ALL': {'MENTION': 'INTERNET'}},
        'merge': False
     },
     # REMOVE MENTION
     {
        # online assessment
        'name': 'ONLINE_ASSESSMENT',
        'pattern': [{'LOWER': {'IN': ['internet', 'online', 'on-line']}}, {'LOWER': {'IN': ['assessment', 'form', 'interview', 'questionaire', 'questionnaire', 'survey', 'assessments', 'forms', 'interview', 'questionaires', 'questionnaires', 'surveys']}}],
        'avm': {'ALL': {'MENTION': False}},
        'merge': False
     },
     {
        # a computer
        'name': 'A_CONPUTER',
        'pattern': [{'LEMMA': 'a'}, {'LEMMA': 'computer'}],
        'avm': {'ALL': {'MENTION': False}},
        'merge': False
     },
     {
        # Online Development and Well Being Assessment
        'name': 'ONLINE_DAWBA',
        'pattern': [{'LEMMA': {'IN': ['online', 'on-line']}}, {'LEMMA': 'development'}, {'LEMMA': 'and'}, {'LEMMA': {'IN': ['wellbeing', 'well-being', 'well']}}, {'LOWER': 'being', 'OP': '?'}, {'LEMMA': {'IN': ['assessment', 'form', 'survey']}}],
        'avm': {'ALL': {'MENTION': False}},
        'merge': False
     },
     {
        # \n PC \n 
        'name': 'NEWLINE_PC_NEWLINE',
        'pattern': [{'POS': 'SPACE'}, {'ORTH': 'PC'}, {'POS': 'SPACE'}],
        'avm': {'ALL': {'MENTION': False}},
        'merge': False
     },
     {
        # PC: Intentional overdose
        'name': 'PC_PUNCT',
        'pattern': [{'ORTH': 'PC'}, {'POS': ':'}],
        'avm': {'ALL': {'MENTION': False}},
        'merge': False
     },
     {
        # computer science
        'name': 'COMPUTER_SCIENCE',
        'pattern': [{'LEMMA': 'computer'}, {'LEMMA': 'science'}],
        'avm': {'ALL': {'MENTION': False}},
        'merge': False
     },
     {
        # Temporary Internet
        'name': 'TEMPORARY_INTERNET_FILES',
        'pattern': [{'LOWER': {'REGEX': '.+temporary.*'}}, {'LOWER': 'internet'}],
        'avm': {'ALL': {'MENTION': False}},
        'merge': False
     },
     {
        # our website
        'name': 'OUR_WEBSITE',
        'pattern': [{'LOWER': 'our'}, {'LEMMA': {'IN': ['website', 'web-site']}}],
        'avm': {'ALL': {'MENTION': False}},
        'merge': False
     },
     {
        # \n web address \n  www.dawba.net
        'name': 'WEB_ADDRESS_NEWLINE_DAWBA',
        'pattern': [{'ORTH': 'PC'}, {'POS': 'SPACE'}, {'LIKE_URL': True}],
        'avm': {'ALL': {'MENTION': False}},
        'merge': False
     },
     {
        # Website : www.camhs.slam.nhs.uk
        'name': 'WEBSITE_URL_1',
        'pattern': [{'LOWER': 'website'}, {'POS': 'SPACE', 'OP': '*'}, {'POS': 'PUNCT'}, {'POS': 'SPACE', 'OP': '*'}, {'LIKE_URL': True, '_': {'LA': {'NOT_IN': ['HEALTH_WEB']}}}],
        'avm': {'ALL': {'MENTION': False}},
        'merge': False
     },
     {
        # website \n <http://www.lambeth.gov.uk/>
        'name': 'WEBSITE_URL_2',
        'pattern': [{'LOWER': 'website'}, {'POS': 'SPACE', 'OP': '*'}, {'POS': 'SPACE', 'OP': '*'}, {}, {'LIKE_URL': True, '_': {'LA': {'NOT_IN': ['HEALTH_WEB']}}}],
        'avm': {'ALL': {'MENTION': False}},
        'merge': False
     },
     {
        # \n Website - blah blah blah
        'name': 'WEBSITE_URL_3',
        'pattern': [{'POS': 'SPACE', 'OP': '+'}, {'LOWER': 'website'}, {'POS': 'SPACE', 'OP': '*'}, {'POS': 'PUNCT'}],
        'avm': {'ALL': {'MENTION': False}},
        'merge': False
     },
     {
        # Please use this website address
        'name': 'PLEASE_USE_WEBSITE_ADDRESS_1',
        'pattern': [{'LOWER': 'please'}, {'LEMMA': 'use'}, {}, {'LEMMA': {'IN': ['internet', 'web', 'website', 'web-site']}}, {'LEMMA': 'address', 'OP': '?'}],
        'avm': {'ALL': {'MENTION': False}},
        'merge': False
     },
     {
        # Please use this web site address
        'name': 'PLEASE_USE_WEBSITE_ADDRESS_2',
        'pattern': [{'LOWER': 'please'}, {'LEMMA': 'use'}, {}, {'LEMMA': 'web'}, {'LEMMA': 'site'}, {'LEMMA': 'address', 'OP': '?'}],
        'avm': {'ALL': {'MENTION': False}},
        'merge': False
     },
     {
        # by logging on to a web address
        'name': 'BY_LOG_ON_TO_WEB_ADDRESS',
        'pattern': [{'LEMMA': 'by'}, {'LEMMA': {'IN': ['log', 'logging']}}, {'LEMMA': {'IN': ['on', 'onto']}}, {}, {'LEMMA': 'web'}, {'LEMMA': 'site', 'OP': '?'}, {'LEMMA': 'address'}],
        'avm': {'ALL': {'MENTION': False}},
        'merge': False
     },
     {
        # the following web address
        'name': 'THE_FOLLOWING_WEB_ADDRESS',
        'pattern': [{'LEMMA': 'the'}, {'LEMMA': {'IN': ['follow', 'following']}}, {'LEMMA': {'IN': ['web', 'website', 'web-site']}}, {'LEMMA': 'site', 'OP': '?'}, {'LEMMA': 'address', 'OP': '?'}],
        'avm': {'ALL': {'MENTION': False}},
        'merge': False
     },
     {
        # have the Internet
        'name': 'HAVE_THE_INTERNET',
        'pattern': [{'LEMMA': 'have'}, {'LEMMA': 'the'}, {'LOWER': 'internet'}],
        'avm': {'ALL': {'MENTION': False}},
        'merge': False
     },
     {
        # Internet access
        'name': 'HAVE_INTERNET',
        'pattern': [{'LOWER': {'IN': ['internet', 'web']}}, {'LEMMA': 'access'}],
        'avm': {'ALL': {'MENTION': False}},
        'merge': False
     },
     {
        # DAWBA online
        'name': 'DAWBA',
        'pattern': [{'LOWER': 'dawba'}, {'_': {'LA': {'IN': ['GAMING', 'INTERNET', 'SOCIAL_MEDIA']}}, 'OP': '+'}],
        'avm': {'ALL': {'MENTION': False}},
        'merge': False
     },
     {
        # online resources
        'name': 'ONLINE_RESOURCES',
        'pattern': [{'LOWER': {'IN': ['online', 'on-line']}}, {'LEMMA': 'resource'}],
        'avm': {'ALL': {'MENTION': False}},
        'merge': False
     },
     {
        # via the Internet
        'name': 'VIA_INTERNET',
        'pattern': [{'LOWER': 'via'}, {'LEMMA': 'the', 'OP': '?'}, {'LOWER': 'internet'}],
        'avm': {'ALL': {'MENTION': False}},
        'merge': False
     }
]