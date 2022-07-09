import re


import re

def sanitize_text(text: str) -> str:
    r"""Sanitizes the text for tts.
        What gets removed:
     - following characters`^_~@!&;#:-%“”‘"%*/{}[]()\|<>?=+`
     - any http or https links

    Args:
        text (str): Text to be sanitized

    Returns:
        str: Sanitized text
    """

    # remove any urls from the text
    regex_urls = r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"

    profanity = [
        ["a word", r"(?:^|\W)ass(?:$|\W)", r"arse", r"asdf", r"asdf", r"asdf"],
        ["b word", r"bastard", r"blow job", r"blowie", r"bitch", r"asdf"],
        ["c word", r"cunt", r"(?:^|\W)cum(?:$|\W)", r"(?:^|\W)coon(?:$|\W)", r"cock", r"clit"],
        ["d word", r"dick", r"asdf", r"asdf", r"asdf", r"asdf"],
        ["e word", r"asdf", r"asdf", r"asdf", r"asdf", r"asdf"],
        ["f word", r"fuck", r"faggot", r"fag", r"asdf", r"asdf"],
        ["g word", r"asdf", r"asdf", r"asdf", r"asdf", r"asdf"],
        ["h word", r"asdf", r"asdf", r"asdf", r"asdf", r"asdf"],
        ["i word", r"asdf", r"asdf", r"asdf", r"asdf", r"asdf"],
        ["j word", r"asdf", r"asdf", r"asdf", r"asdf", r"asdf"],
        ["k word", r"knob", r"kum", r"koon", r"asdf", r"asdf"],
        ["l word", r"asdf", r"asdf", r"asdf", r"asdf", r"asdf"],
        ["m word", r"minge", r"(?:^|\W)mong(?:$|\W)", r"motherfucker", r"asdf", r"asdf"],
        ["n word", r"nigga", r"nigger", r"asdf", r"asdf", r"asdf"],
        ["o word", r"asdf", r"asdf", r"asdf", r"asdf", r"asdf"],
        ["p word", r"pussy", r"piss", r"punani", r"prick", r"asdf"],
        ["q word", r"asdf", r"asdf", r"asdf", r"asdf", r"asdf"],
        ["r word", r"retard", r"retards", r"asdf", r"asdf", r"asdf"],
        ["s word", r"slut", r"shit", r"asdf", r"asdf", r"asdf"],
        ["t word", r"twat", r"(?:^|\W)tit(?:$|\W)", r"(?:^|\W)tits(?:$|\W)", r"titties", r"asdf"],
        ["u word", r"asdf", r"asdf", r"asdf", r"asdf", r"asdf"],
        ["v word", r"asdf", r"asdf", r"asdf", r"asdf", r"asdf"],
        ["w word", r"wanker", r"asdf", r"asdf", r"asdf", r"asdf"],
    ]

    result = re.sub(regex_urls, " ", text)

    # note: not removing apostrophes
    regex_expr = r"\s['|’]|['|’]\s|[\^_~@!&;#:\-%“”‘\"%\*/{}\[\]\(\)\\|<>=+]"
    result = re.sub(regex_expr, " ", result)
    result = result.replace("+", "plus").replace("&", "and")
    for x in range(0, len(profanity)):
        for y in range(1, len(profanity[0])):
            # print("row: " + str(x))
            # print("column: " + str(y))
            result = re.sub(profanity[x][y], profanity[x][0], result)
            # print(regex[x][y])
    # remove extra whitespace
    print(result)
    return " ".join(result.split())

