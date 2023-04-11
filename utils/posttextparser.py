import re

import spacy

from utils.console import print_step
from utils.voice import sanitize_text


# working good
def posttextparser(obj):
    text = re.sub("\n", "", obj)

    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print_step(
            "The spacy model can't load. You need to install it with the command \npython -m spacy download en_core_web_sm"
        )
        exit()

    doc = nlp(text)

    newtext: list = []

    # to check for space str
    for line in doc.sents:
        if sanitize_text(line.text):
            newtext.append(line.text)
            # print(line)

    return newtext
