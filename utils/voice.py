import re


def sanitize_text(text):
    """
    Sanitizes the text for tts.
    What gets removed:
    - following characters`^_~@!&;#:-%“”‘"%*/{}[]()\|<>?=+`
    """

    # note: not removing apostrophes
    regex_expr = r"\s['|’]|['|’]\s|[\^_~@!&;#:\-%“”‘\"%\*/{}\[\]\(\)\\|<>=+]"
    result = re.sub(regex_expr, " ", text)

    # remove extra whitespace
    return " ".join(result.split())
