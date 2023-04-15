import openai
from utils import settings
from utils.console import print_step


def shorten_filename(filename: str):
    print_step("Now asking ChatGPT to shorten the filename")
    openai.api_key = settings.config["ai"]["openai_api_key"]
    # Use OpenAI to generate a shorter name that captures the essence of the original name
    prompt = f"Create a new filename for the given file \"{filename}\" that is both descriptive and concise. The new filename should be no more than 95 characters in length and should not include any special characters or file extensions. Instead, focus on capturing the essence of the original name in a creative and attention-grabbing way. Avoid using generic terms and instead opt for a name that is both meaningful and memorable. Be sure to strike a balance between being humorous and staying true to the original name. Let your creativity shine!"
    completions = openai.ChatCompletion.create(
        model=settings.config["ai"]["openai_model"],
        messages=[{"role": "user", "content": prompt}]
    )
    filename = completions["choices"][0]["message"]["content"].strip().strip('"')
    not_permitted_chars = ["<", ">", ":", "\"", "/", "\\", "|", "?", "*", "."]
    for char in not_permitted_chars:
        filename = filename.replace(char, "")
    return filename

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
            model=settings.config["ai"]["openai_model"], messages=messages
        )
    reply = chat.choices[0].message.content
    print(f"ChatGPT: {reply}")
    path = f"results/{subreddit}/{filename}"
    path = path[:251]
    path = path + ".txt"
    with open(path, 'w', encoding="utf-8") as f:
        f.write(reply)
