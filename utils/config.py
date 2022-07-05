# write a class that takes .env file and parses it into a dictionary
from dotenv import dotenv_values

DEFAULTS = {
    "SUBREDDIT": "AskReddit",
    "ALLOW_NSFW": "False",
    "POST_ID": "",
    "THEME": "DARK",
    "REDDIT_2FA": "no",
    "TIMES_TO_RUN": "",
    "MAX_COMMENT_LENGTH": "500",
    "OPACITY": "1",
    "VOICE": "en_us_001",
    "STORYMODE": "False",
}


class Config:
    def __init__(self):
        self.raw = dotenv_values("../.env")
        self.load_attrs()

    def __getattr__(self, attr):  # code completion for attributes fix.
        return getattr(self, attr)

    def load_attrs(self):
        for key, value in self.raw.items():
            self.add_attr(key, value)

    def add_attr(self, key, value):
        if value is None or value == "":
            setattr(self, key, DEFAULTS[key])
        else:
            setattr(self, key, str(value))


config = Config()

print(config.SUBREDDIT)
# def temp():
#    root = ''
#    if isinstance(root, praw.models.Submission):
#        root_type = 'submission'
#    elif isinstance(root, praw.models.Comment):
#        root_type = 'comment'
#
