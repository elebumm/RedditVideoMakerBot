import re
from typing import List

from utils import settings


# working good
def split_text(obj) -> List[str]:
    text: str = re.sub("\n", " ", obj)

    words_on_screen = settings.config["settings"]["words_on_screen"]
    
    words = text.split()
    grouped_words = [' '.join(words[i: i + words_on_screen]) for i in range(0, len(words), words_on_screen)]

    return grouped_words
