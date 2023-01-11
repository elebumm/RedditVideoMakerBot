# Frequently Asked Questions

- [Main.py Not Working](#Main.py-is-not-working)
- [Easy Way To Edit Config](#easy-way-to-edit-config)
- [Read PThe Post Not Just The Title](#some-of-my-markdown-elements-arent-highlighted)
- [TikTok Reader Crashing](#tiktok-reader-crashing)
- [Preview TTS Voice](#preview-tts-voice)
- [Could Not Concat Numpy.float64](#could-not-concat-numpyfloat64)
- [Video Length Is Too Long & I Am Too Lazy To Edit It Myself](#video-length-is-too-long--i-am-too-lazy-to-edit-it-myself)
- [TikTok SessionId Expiring](#tiktok-sessionid-expiring)
- [Main.py Crashing Due To Video Length](#mainpy-crashing-due-to-video-length)

## Mainpy is not working

The most common occurence is the use of an incorrect Python version, or a missing dependency. Make sure you have Python 3.10 installed, and that you have installed the dependencies using `pip install -r requirements.txt`. If you are still having trouble, feel free to ask for help in the [Discord](https://discord.gg/QaTx2ZDqea)

## Easy Way To Edit Config

Run `GUI.py` this opens a web editor in which you can edit the config file. You can also preview the TTS voices.

## Read the post not just the title

The bot by default will only read the title of the post. If you want to read the post as well, you can change the `storymode` option in the `config.toml` file to `true`. This will make the bot read the post as well as the title.

## TikTok SessionId Expiring

It is, what it is - head to TikTok and log in, then copy the `sessionid` cookie from the browser and paste it into the `config.toml` file. Or you can write a script to do this for you :)

## TikTok Reader Crashing

TikTok TTS has a maximum character limit, ~2000. If you are getting a crash, it is likely that the post is too long. You can change the `voice_choice` option in the `config.toml` file to `streamlabs`.

## Preview TTS Voice

Run the `GUI.py` - it will open a browser window with a GUI option to change settings. You can click on the `Settings` button in the header and click on the `Speaker` icon next to each applicable option to preview the voice.

## NSFW Posts Not Working

By default NSFW is disabled. To enable it, you can change the `allow_nsfw` option in the `config.toml` file to `true`. This will make the bot read NSFW posts as well as SFW posts. 

**NOTE:** This needs to be enable on the Reddit account used to create the app.

## Could Not Concat Numpy.float64

This is due to the `utils/backgrounds.json` ; temporary solution is to edit the third parameter of the video in the array to be a string instead of a float. Proper solution would be to ensure we are typecasting the values in the `video_creation/backgrounds.py` file.

## Video Length Is Too Long & I Am Too Lazy To Edit It Myself

Seriously, I mean thats what I did but fine fair enough - in `/video_creation/final_video.py` you can cap the input length of the `make_final_video` function.

## Mainpy Crashing Due To Video Length

This is mostlikely due to a corrupt video - remove the files from `assets/backgrounds`