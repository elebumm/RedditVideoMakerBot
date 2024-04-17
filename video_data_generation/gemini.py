import google.generativeai as genai
from utils import settings


genai.configure(api_key=settings.config["settings"]["gemini"]["gemini_api_key"])

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

        Background audio by - {audio_credits}
        Background video by - {video_credits}
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

if __name__ == '__main__':
    post = """

This is my dads story. With all of the weirdest things that have happened, this one takes the cake.

My dad doesn't really speak of many paranormal experiences. This one freaked him out enough though, that he told me. One night, he went to bed with my mom and their dogs. My dad falls asleep pretty fast but for some reason that night, he couldn't.

Some background info: My parents at the time had two cats, Sweetpea and Baby Princess( my sister named her when she was 6) Their cats would sometimss go into their room when they were sleeping. My parents always slept with their door open(I could never, creeps me out). Their room is the first room when you would reach the top of the steps.

Anyways, my dad was laying in bed tossing and turning. He flipped on his back and closed his eyes. When he was laying there, he felt a pressure going up his legs. He figured the cats were walking up his legs. He then realized the pressure was going up his legs and ended up to his chest. He couldn't move a muscle. That's when he started to choke. His eyes popped open and he looked over and there was a figure standing over him with his hands around my dads throat.

According to my dad, the figure had a black WW2 Nazi uniform on with the black uniform hat that had a swastika on it. The choking lasted for some time until my dad told it to get the fuck off of him, then it disappeared. My dad was freaked out. He got up and checked inside all of our bedrooms and throughout the house but couldn't find anyone anywhere. Everyone was asleep.

I asked my dad why he thought the Nazi was choking him. He said he wasn't sure why, maybe he was an old angry relative. My grandma grew up in Germany through the war and my grandmas dad was a Nazi. So to say the least, we had some relatives that were in the war. I'm not sure why this ghost attacked my dad, maybe because he was the strongest in the house? Who knows.

My dad isn't one to make up stories like this, so I believe him. He's a very strong and brave man, and it takes a lot for him to get scared. He told me that this really got to him and that he was scared for us and this is why he got up and searched throughout the house. Usually, if paranormal things happen, he doesn't say much because he didn't want to scare us when we were kids.

I know that some of you might think that he had sleep paralysis when this happened, but my dad did not suffer from this. He told me that this was the first and only time that he couldn't move like this.

Thank you for reading! Let me know what you guys think :)
"""
    for i in get_video_data(post):
        print(i, end="\n\n")