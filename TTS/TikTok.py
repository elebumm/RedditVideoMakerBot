import random
import time
from typing import Optional, Final
import requests, base64, re, sys
from threading import Thread
from playsound import playsound

from utils import settings

# define the endpoint data with URLs and corresponding response keys
ENDPOINT_DATA = [
    {
        "url": "https://tiktok-tts.weilnet.workers.dev/api/generation",
        "response": "data"
    },
    {
        "url": "https://countik.com/api/text/speech",
        "response": "v_data"
    },
    {
        "url": "https://gesserit.co/api/tiktok-tts",
        "response": "base64"
    }
]

# define available voices for text-to-speech conversion
VOICES = [
    # DISNEY VOICES
    'en_us_ghostface',            # Ghost Face
    'en_us_chewbacca',            # Chewbacca
    'en_us_c3po',                 # C3PO
    'en_us_stitch',               # Stitch
    'en_us_stormtrooper',         # Stormtrooper
    'en_us_rocket',               # Rocket
    # ENGLISH VOICES
    'en_au_001',                  # English AU - Female
    'en_au_002',                  # English AU - Male
    'en_uk_001',                  # English UK - Male 1
    'en_uk_003',                  # English UK - Male 2
    'en_us_001',                  # English US - Female (Int. 1)
    'en_us_002',                  # English US - Female (Int. 2)
    'en_us_006',                  # English US - Male 1
    'en_us_007',                  # English US - Male 2
    'en_us_009',                  # English US - Male 3
    'en_us_010',                  # English US - Male 4
    # EUROPE VOICES
    'fr_001',                     # French - Male 1
    'fr_002',                     # French - Male 2
    'de_001',                     # German - Female
    'de_002',                     # German - Male
    'es_002',                     # Spanish - Male
    # AMERICA VOICES
    'es_mx_002',                  # Spanish MX - Male
    'br_001',                     # Portuguese BR - Female 1
    'br_003',                     # Portuguese BR - Female 2
    'br_004',                     # Portuguese BR - Female 3
    'br_005',                     # Portuguese BR - Male
    # ASIA VOICES
    'id_001',                     # Indonesian - Female
    'jp_001',                     # Japanese - Female 1
    'jp_003',                     # Japanese - Female 2
    'jp_005',                     # Japanese - Female 3
    'jp_006',                     # Japanese - Male
    'kr_002',                     # Korean - Male 1
    'kr_003',                     # Korean - Female
    'kr_004',                     # Korean - Male 2
    # SINGING VOICES
    'en_female_f08_salut_damour',  # Alto
    'en_male_m03_lobby',           # Tenor
    'en_female_f08_warmy_breeze',  # Warmy Breeze
    'en_male_m03_sunshine_soon',   # Sunshine Soon
    # OTHER
    'en_male_narration',           # narrator
    'en_male_funny',               # wacky
    'en_female_emotional',         # peaceful
]

class TikTok:
    """TikTok Text-to-Speech Wrapper"""

    def __init__(self):
        # Set the headers for the requests
        headers = {
            "User-Agent": "com.zhiliaoapp.musically/2022600030 (Linux; U; Android 7.1.2; es_ES; SM-G988N; "
            "Build/NRD90M;tt-ok/3.12.13.1)",
            "Cookie": f"sessionid={settings.config['settings']['tts']['tiktok_sessionid']}",
        }

        # Set the base URL for the TikTok API
        self.URI_BASE = "https://api16-normal-c-useast1a.tiktokv.com/media/api/text/speech/invoke/"

        # Set the maximum number of characters allowed for text-to-speech conversion
        self.max_chars = 200

        # Create a new requests session with the specified headers
        self._session = requests.Session()
        self._session.headers = headers

    def run(self, text: str, filepath: str, random_voice: bool = False, play_sound: bool = False):
        # If random_voice is True, assign a random voice from the VOICES list to the voice variable
        # Otherwise, get the voice from the settings config or set it to None if not found
        if random_voice:
            voice = self.random_voice()
        else:
            voice = settings.config["settings"]["tts"].get("tiktok_voice", None)

        # Split the text into chunks of up to 300 characters
        chunks = self._split_text(text)

        # Iterate over the ENDPOINT_DATA list
        for entry in ENDPOINT_DATA:
            endpoint_valid = True  # Flag to track if the current endpoint is valid
            audio_data = ["" for _ in range(len(chunks))]  # Initialize a list to store audio data for each chunk

            # Define a function to generate audio for a single chunk
            def generate_audio_chunk(index: int, chunk: str) -> None:
                nonlocal endpoint_valid  # Use the outer variable endpoint_valid
                if not endpoint_valid:
                    return  # If the endpoint is invalid, skip this chunk

                try:
                    # Send a POST request to the endpoint with the text and voice parameters
                    response = requests.post(
                        entry["url"],
                        json={
                            "text": chunk,
                            "voice": voice
                        }
                    )

                    if response.status_code == 200:
                        # If the request is successful, store the audio data in the audio_data list
                        audio_data[index] = response.json()[entry["response"]]
                    else:
                        # If the request fails, mark the endpoint as invalid
                        endpoint_valid = False

                except requests.RequestException as e:
                    print(f"Error: {e}")
                    sys.exit()  # Exit the program if there's an error

            # Create and start threads to generate audio for each chunk in parallel
            threads = []
            for index, chunk in enumerate(chunks):
                thread = Thread(target=generate_audio_chunk, args=(index, chunk))
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            if not endpoint_valid:
                continue  # If the endpoint is invalid, try the next one

            # Combine the audio data for all chunks and decode the base64 data
            audio_bytes = base64.b64decode("".join(audio_data))

            # Write the audio data to the specified file
            with open(filepath, "wb") as file:
                file.write(audio_bytes)
                print(f"File '{filepath}' has been generated successfully.")

            # If play_sound is True, play the generated audio file
            if play_sound:
                playsound(filepath)

            break  # Exit the loop if audio generation is successful
    def _split_text(self, text: str) -> list[str]:
        # Initialize an empty list to store the merged chunks
        merged_chunks: list[str] = []
        
        # Use a regular expression to split the text into chunks based on punctuation marks
        seperated_chunks: list[str] = re.findall(r'.*?[.,!?:;-]|.+', text)

        # Iterate over the separated chunks
        for i, chunk in enumerate(seperated_chunks):
            # If the chunk is longer than 300 characters
            if len(chunk) > 300:
                # Split the chunk further into smaller chunks based on spaces
                seperated_chunks[i:i+1] = re.findall(r'.*?[ ]|.+', chunk)

        # Initialize an empty string to store the current merged chunk
        merged_chunk = ""
        # Iterate over the separated chunks
        for seperated_chunk in seperated_chunks:
            # If adding the current chunk to the merged chunk won't exceed 300 characters
            if len(merged_chunk) + len(seperated_chunk) <= 300:
                # Append the current chunk to the merged chunk
                merged_chunk += seperated_chunk
            else:
                # Otherwise, add the current merged chunk to the list of merged chunks
                merged_chunks.append(merged_chunk)
                # And start a new merged chunk with the current chunk
                merged_chunk = seperated_chunk

        # Add the final merged chunk to the list of merged chunks
        merged_chunks.append(merged_chunk)

        # Return the list of merged chunks
        return merged_chunks

    @staticmethod
    def random_voice() -> str:
        # Return a randomly selected voice from the VOICES list
        return random.choice(VOICES)
