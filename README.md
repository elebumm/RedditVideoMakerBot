# Reddit Video Maker Bot 🎥

All done WITHOUT video editing or asset compiling. Just pure ✨programming magic✨.

Created by Lewis Menelaws & [TMRRW](https://tmrrwinc.ca)

<a target="_blank" href="https://tmrrwinc.ca">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://user-images.githubusercontent.com/6053155/170528535-e274dc0b-7972-4b27-af22-637f8c370133.png">
  <source media="(prefers-color-scheme: light)" srcset="https://user-images.githubusercontent.com/6053155/170528582-cb6671e7-5a2f-4bd4-a048-0e6cfa54f0f7.png">
  <img src="https://user-images.githubusercontent.com/6053155/170528582-cb6671e7-5a2f-4bd4-a048-0e6cfa54f0f7.png" width="350">
</picture>

</a>

## Video Explainer

[![lewisthumbnail](https://user-images.githubusercontent.com/6053155/173631669-1d1b14ad-c478-4010-b57d-d79592a789f2.png)
](https://www.youtube.com/watch?v=3gjcY_00U1w)

## Motivation 🤔

These videos on TikTok, YouTube and Instagram get MILLIONS of views across all platforms and require very little effort.
The only original thing being done is the editing and gathering of all materials...

... but what if we can automate that process? 🤔

## Disclaimers 🚨

- **At the moment**, this repository won't attempt to upload this content through this bot. It will give you a file that
  you will then have to upload manually. This is for the sake of avoiding any sort of community guideline issues.

## Requirements

- Python 3.6+
- Playwright (this should install automatically in installation)
- Sox

## Installation 👩‍💻

1. Clone this repository
2. 2a **Automatic Install**: Run `python main.py` and type 'yes' to activate the setup assistant.

   2b **Manual Install**: Rename `.env.template` to `.env` and replace all values with the appropriate fields. To get Reddit keys (**required**), visit [the Reddit Apps page.](https://www.reddit.com/prefs/apps) TL;DR set up an app that is a "script". Copy your keys into the `.env` file, along with whether your account uses two-factor authentication.

3. Install [SoX](https://sourceforge.net/projects/sox/files/sox/)
   
4. Run `pip install -r requirements.txt`

5. Run `playwright install` and `playwright install-deps`. (if this fails try adding python -m to the front of the command)

6. Run `python main.py` (unless you chose automatic install, then the installer will automatically run main.py)
   required\*\*), visit [the Reddit Apps page.](https://www.reddit.com/prefs/apps) TL;DR set up an app that is a "script".
   Copy your keys into the `.env` file, along with whether your account uses two-factor authentication.
7. Enjoy 😎

(Note if you got an error installing or running the bot try first rerunning the command with a three after the name e.g. python3 or pip3)
## Video

https://user-images.githubusercontent.com/66544866/173453972-6526e4e6-c6ef-41c5-ab40-5d275e724e7c.mp4

## Contributing & Ways to improve 📈

In its current state, this bot does exactly what it needs to do. However, lots of improvements can be made.

I have tried to simplify the code so anyone can read it and start contributing at any skill level. Don't be shy :) contribute!

- [ ] Creating better documentation and adding a command line interface.
- [x] Allowing users to choose a reddit thread instead of being randomized.
- [x] Allowing users to choose a background that is picked instead of the Minecraft one.
- [x] Allowing users to choose between any subreddit.
- [x] Allowing users to change voice.
- [x] Checks if a video has already been created
- [x] Light and Dark modes
- [x] NSFW post filter

Please read our [contributing guidelines](CONTRIBUTING.md) for more detailed information.

## Developers and maintainers.

Elebumm (Lewis#6305) - https://github.com/elebumm (Founder)

Jason (JasonLovesDoggo#1904) - https://github.com/JasonLovesDoggo

CallumIO (c.#6837) - https://github.com/CallumIO

HarryDaDev (hrvyy#9677) - https://github.com/ImmaHarry

LukaHietala (Pix.#0001) - https://github.com/LukaHietala

Freebiell (Freebie#6429) - https://github.com/FreebieII
