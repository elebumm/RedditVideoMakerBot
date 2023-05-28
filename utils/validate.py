import sys
from typing import NoReturn

from utils import settings
from utils.console import print_substep


def validat_env(obj) -> NoReturn | None:
    """
    check for wrong
    """
    if (
          settings.config["settings"]["tts"]["tiktok_sessionid"] == ""
         and settings.config["settings"]["tts"]["voice_choice"] == "tiktok"
         ):
        print_substep(
            "TikTok voice requires a sessionid! Check our documentation on how to obtain one.",
            "bold red",
        )
        sys.exit()