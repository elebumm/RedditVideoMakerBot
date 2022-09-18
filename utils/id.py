import re

from utils.console import print_substep


def id(reddit_obj: dict):
    """
    This function takes a reddit object and returns the post id
    """
    id = re.sub(r"[^\w\s-]", "", reddit_obj["thread_id"])
    print_substep(f"Thread ID is {id}", style="bold blue")
    return id
