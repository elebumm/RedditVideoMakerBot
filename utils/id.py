import re
from typing import Optional

from utils.console import print_substep


def extract_id(reddit_obj: dict, field: Optional[str] = "thread_id"):
    """
    This function takes a reddit object and returns the post id
    """
    if field not in reddit_obj.keys():
        raise ValueError(f"Field '{field}' not found in reddit object")
    reddit_id = re.sub(r"[^\w\s-]", "", reddit_obj[field])
    return reddit_id
