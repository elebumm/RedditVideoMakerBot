import google.generativeai as genai
from utils import settings


genai.configure(api_key=settings.config["ai"]["gemini_api_key"])

prompt1 = """I make some youtube videos where I get subreddits about ghost stories and make a video of it.
    I will send a post to you and you should generate a YouTube video title, tags and description for it.
    Also generate a short, relevant and catchy text to be written on the video thumbnail.
    Only respond with the following:
    title::: "The video title"
    description::: "The video description"
    tags::: "The video tags" without hashtags and separated by commas
    thumbnail_text::: "The text to be wriiten on the video thumbnail"
    
    Here is the post:
    """

prompt2 = """Describe a thumbnail for a youtube video about ghosts and ghost stories.
Only respond with the thumbnail description.
The description should be clear for an AI image generator model to generate it.

The video description:
"""

default_tags = [
    "scary stories",
    "horror stories",
    "true scary stories",
    "ghost stories",
    "true horror stories",
    "scary story",
    "scary",
    "creepy stories",
    "horror story",
    "true stories",
    "scary true stories",
    "true ghost stories",
    "paranormal stories",
    "disturbing",
    "scary video",
    "ghost",
    "true paranormal stories",
    "true scary",
    "scary true",
]

description_tags = "#Creepy #Scarystories #paranormal #supernatural #horrorstories #creepystories #truescary_stories #reddit_horror_stories #true_horror_stories\n"

model = genai.GenerativeModel('gemini-pro')

def get_credits(bg_config):
    audio_credits = bg_config['audio'][-1]
    video_credits = bg_config['video'][-2]
    credits_template = f"""

Background audio by - @{audio_credits}
Background video by - @{video_credits}
"""
    return credits_template

def get_data(post):
    response = model.generate_content(prompt1 + post)

    # print("Data:", response.prompt_feedback)
    text = response.text.split('\n')
    data = {i.split(':::')[0].strip(): i.split(':::')[1].strip() for i in text}
    return data

def get_thumbnail(post):
    thumbnail_response = model.generate_content(prompt2 + post)
    # print('Thumbnail:', thumbnail_response.prompt_feedback)
    return thumbnail_response.text

def get_video_data(post, bg_config):
    data = None
    thumbnail = None
    print("Generating video title & description...")
    for i in range(3):
        if i != 0: print("Try:", i+1)
        try:
            if data is None: data = get_data(post)
            if data and thumbnail is None:
                thumbnail = get_thumbnail(data['tags'])
            break
        except Exception as e:
            print(e)
            continue
    
    if data:
        data['title'] = "True Scary Stories | " + data['title']
        data['description'] = description_tags + data['description'] + get_credits(bg_config)
        data['tags'] = data['tags'] + ', ' + ', '.join(default_tags)
    return data, thumbnail
