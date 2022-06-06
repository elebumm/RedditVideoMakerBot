import re


def sanitize_text(text):
    """
    Sanitizes the text for tts.
       What gets removed:
    - following characters`^_~@!&;#:-%“”‘"%*/{}[]()\|<>?=+`
    - any http or https links
    """

    # remove any urls from the text
    regex_urls = r"((http|https)://[^\s]+)"
    result = re.sub(regex_urls, " ", text)

    # note: not removing apostrophes
    regex_expr = r"\s['|’]|['|’]\s|[\^_~@!&;#:\-%“”‘\"%\*/{}\[\]\(\)\\|<>=+]"
    result = re.sub(regex_expr, " ", result)

    # remove extra whitespace
    return " ".join(result.split())
