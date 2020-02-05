from spacy.tokens import Token

#################################
# Custom attribute declarations #
#################################

Token.set_extension('TEST', default=False, force=True)


#################################
# Token sequence rules, Level 0 #
#################################

"""
    Rules to annotate test example (in token_sequence_annotator.py main):
    She and her brother play games online and use the Internet a lot, for example,
    they go on Youtube and play MineCraft and chat online a lot while they play
    video games at home.
"""

TEST_RULES = [
    {
        # play games
        'name': 'PLAY_GAMES',
        'pattern': [{'LEMMA': 'play'}, {'LEMMA': 'video', 'OP': '?'}, {'LEMMA': 'game'}, {'LEMMA': 'online', 'OP': '?'}],
        'avm': {'ALL': {'TEST': 'OK'}},
        'merge': False
    },
    {
        # Internet
        'name': 'INTERNET',
        'pattern': [{'ORTH': {'REGEX': '([Ii]nternet|[Yy]ou[Tt]ube|[Mm]ine[Cc]raft)'}}],
        'avm': {'ALL': {'TEST': 'OK'}},
        'merge': False
    },
    {
        # chat online
        'name': 'CHAT',
        'pattern': [{'LEMMA': {'IN': ['talk', 'chat']}}, {'LEMMA': 'online'}],
        'avm': {'ALL': {'TEST': 'OK'}},
        'merge': False
    }
]