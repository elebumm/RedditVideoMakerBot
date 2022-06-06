import base64

import requests
from gtts import gTTS
from pathlib import Path
from mutagen.mp3 import MP3
from utils.console import print_step, print_substep
from rich.progress import track

voices = [
    # DISNEY VOICES
    'en_us_ghostface',  # Ghost Face
    'en_us_chewbacca',  # Chewbacca
    'en_us_c3po',  # C3PO
    'en_us_stitch',  # Stitch
    'en_us_stormtrooper',  # Stormtrooper
    'en_us_rocket',  # Rocket

    # ENGLISH VOICES
    'en_au_001',  # English AU - Female
    'en_au_002',  # English AU - Male
    'en_uk_001',  # English UK - Male 1
    'en_uk_003',  # English UK - Male 2
    'en_us_001',  # English US - Female (Int. 1)
    'en_us_002',  # English US - Female (Int. 2)
    'en_us_006',  # English US - Male 1
    'en_us_007',  # English US - Male 2
    'en_us_009',  # English US - Male 3
    'en_us_010',  # English US - Male 4

    # EUROPE VOICES
    'fr_001',  # French - Male 1
    'fr_002',  # French - Male 2
    'de_001',  # German - Female
    'de_002',  # German - Male
    'es_002',  # Spanish - Male

    # AMERICA VOICES
    'es_mx_002',  # Spanish MX - Male
    'br_001',  # Portuguese BR - Female 1
    'br_003',  # Portuguese BR - Female 2
    'br_004',  # Portuguese BR - Female 3
    'br_005',  # Portuguese BR - Male

    # ASIA VOICES
    'id_001',  # Indonesian - Female
    'jp_001',  # Japanese - Female 1
    'jp_003',  # Japanese - Female 2
    'jp_005',  # Japanese - Female 3
    'jp_006',  # Japanese - Male
    'kr_002',  # Korean - Male 1
    'kr_003',  # Korean - Female
    'kr_004',  # Korean - Male 2

    # NARRATOR
    'en_male_narration'

    # SINGING VOICES
    'en_female_f08_salut_damour'  # Alto
    'en_male_m03_lobby'  # Tenor
]

def tts(text_speaker: str = 'en_au_001', req_text: str = 'TikTok Text to Speech', filename: str = 'voice.mp3'):
    req_text = req_text.replace("+", "plus")
    req_text = req_text.replace(" ", "+")
    req_text = req_text.replace("&", "and")

    url = f"https://api16-normal-useast5.us.tiktokv.com/media/api/text/speech/invoke/?text_speaker={text_speaker}&req_text={req_text}&speaker_map_type=0"

    r = requests.post(url)

    vstr = [r.json()["data"]["v_str"]][0]
    msg = [r.json()["message"]][0]

    b64d = base64.b64decode(vstr)

    out = open(filename, "wb")
    out.write(b64d)
    out.close()

    return msg.capitalize()

def save_text_to_mp3(reddit_obj):
    """Saves Text to MP3 files.

    Args:
        reddit_obj : The reddit object you received from the reddit API in the askreddit.py file.
    """
    print_step("Saving Text to MP3 files 🎶")
    length = 0

    # Create a folder for the mp3 files.
    Path("assets/mp3").mkdir(parents=True, exist_ok=True)

    #tts = gTTS(text=reddit_obj["thread_title"], lang="en", slow=False, tld="com.au")
    # tts.save(f"assets/mp3/title.mp3")

    tts('en_us_010', reddit_obj["thread_title"], f"assets/mp3/title.mp3")
    length += MP3(f"assets/mp3/title.mp3").info.length

    idx = 0
    too_long_comments = []
    for comment in track(enumerate(reddit_obj["comments"]), "Saving..."):
        # ! Stop creating mp3 files if the length is greater than 50 seconds. This can be longer, but this is just a good starting point
        if length > 50:
            break
        #tts = gTTS(text=comment["comment_body"], lang="en")
        #tts.save(f"assets/mp3/{idx}.mp3")
        response = tts('en_uk_001', comment[1]["comment_body"], f"assets/mp3/{idx}.mp3")
        if response == 'Text too long to create speech audio':
            too_long_comments.append(comment[1])
            continue

        length += MP3(f"assets/mp3/{idx}.mp3").info.length
        idx+=1
    for comment in too_long_comments:
        reddit_obj["comments"].remove(comment)


    print_substep("Saved Text to MP3 files Successfully.", style="bold green")
    # ! Return the index so we know how many screenshots of comments we need to make.
    return length, idx
