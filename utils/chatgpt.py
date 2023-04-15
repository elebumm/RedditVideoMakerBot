import openai
from utils import settings
from utils.console import print_step


def get_video_details(
    subreddit: str, filename: str, reddit_title: str
):
    """Gets a title, description and tags from chatGPT and saves as a txt file

    Args:
        @param subreddit:
        @param reddit_title:
    """
    print_step("Now asking ChatGPT for Video Details")
    openai.api_key = settings.config["ai"]["openai_api_key"]
    messages = [ {"role": "system", "content": 
              "You are a intelligent assistant."} ]
    messages.append(
            {"role": "user", "content": "I would like you to supply a video title, description and tags comma-separated for a video about: " + reddit_title},
        )
    chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )
    reply = chat.choices[0].message.content
    print(f"ChatGPT: {reply}")
    path = f"results/{subreddit}/{filename}"
    path = path[:251]
    path = path + ".txt"
    with open(path, 'w', encoding="utf-8") as f:
        f.write(reply)
