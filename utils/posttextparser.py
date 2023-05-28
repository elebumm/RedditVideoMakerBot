import os
import re
import time
from typing import List

import spacy

from utils.console import print_step
from utils.voice import sanitize_text


# working good
def posttextparser(obj, *, tried: bool = False) -> List[str]:
    text: str = re.sub("\n", " ", obj)
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError as e:
        if not tried:
            os.system("python -m spacy download en_core_web_sm")
            time.sleep(5)
            return posttextparser(obj, tried=True)
        print_step(
            "The spacy model can't load. You need to install it with the command \npython -m spacy download en_core_web_sm "
        )
        raise e

    doc = nlp(text)

    newtext: list = []

    for line in doc.sents:
        if sanitize_text(line.text):
            newtext.append(line.text)

    return newtext
