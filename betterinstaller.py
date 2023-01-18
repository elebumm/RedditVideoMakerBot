
#   ____  ____  _  _  ___      ____  ____  ____  ____  ____  ____      ____  _  _  ___  ____   __    __    __    ____  ____
#  ( ___)(_  _)( \( )/ __)    (  _ \( ___)(_  _)(_  _)( ___)(  _ \    (_  _)( \( )/ __)(_  _) /__\  (  )  (  )  ( ___)(  _ \
#   )__)  _)(_  )  ( \__ \     ) _ < )__)   )(    )(   )__)  )   /     _)(_  )  ( \__ \  )(  /(__)\  )(__  )(__  )__)  )   /
#  (__)  (____)(_)\_)(___/    (____/(____) (__)  (__) (____)(_)\_)    (____)(_)\_)(___/ (__)(__)(__)(____)(____)(____)(_)\_)


#    ______ _              ____       _   _               _____           _        _ _
#   |  ____(_)            |  _ \     | | | |             |_   _|         | |      | | |
#   | |__   _ _ __  ___   | |_) | ___| |_| |_ ___ _ __     | |  _ __  ___| |_ __ _| | | ___ _ __
#   |  __| | | '_ \/ __|  |  _ < / _ \ __| __/ _ \ '__|    | | | '_ \/ __| __/ _` | | |/ _ \ '__|
#   | |    | | | | \__ \  | |_) |  __/ |_| ||  __/ |      _| |_| | | \__ \ || (_| | | |  __/ |
#   |_|    |_|_| |_|___/  |____/ \___|\__|\__\___|_|     |_____|_| |_|___/\__\__,_|_|_|\___|_|
#
#
import time
import os



# This is how we run commands.
def runcmd(cmd):
    os.system(cmd)
def endmsg():
    unvclr()
    print("Thanks for using betterinstaller! Hopefully this worked fine! Goodbye! -Fin-Github")
    print(" ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄        ▄  ▄▄▄▄▄▄▄▄▄▄▄            ▄▄▄▄▄▄▄▄▄▄   ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄            ▄▄▄▄▄▄▄▄▄▄▄  ▄▄        ▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄            ▄            ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄\n▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░▌      ▐░▌▐░░░░░░░░░░░▌          ▐░░░░░░░░░░▌ ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌          ▐░░░░░░░░░░░▌▐░░▌      ▐░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌          ▐░▌          ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌\n▐░█▀▀▀▀▀▀▀▀▀  ▀▀▀▀█░█▀▀▀▀ ▐░▌░▌     ▐░▌▐░█▀▀▀▀▀▀▀▀▀           ▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀▀▀  ▀▀▀▀█░█▀▀▀▀  ▀▀▀▀█░█▀▀▀▀ ▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌           ▀▀▀▀█░█▀▀▀▀ ▐░▌░▌     ▐░▌▐░█▀▀▀▀▀▀▀▀▀  ▀▀▀▀█░█▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌▐░▌          ▐░▌          ▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌\n▐░▌               ▐░▌     ▐░▌▐░▌    ▐░▌▐░▌                    ▐░▌       ▐░▌▐░▌               ▐░▌          ▐░▌     ▐░▌          ▐░▌       ▐░▌               ▐░▌     ▐░▌▐░▌    ▐░▌▐░▌               ▐░▌     ▐░▌       ▐░▌▐░▌          ▐░▌          ▐░▌          ▐░▌       ▐░▌\n▐░█▄▄▄▄▄▄▄▄▄      ▐░▌     ▐░▌ ▐░▌   ▐░▌▐░█▄▄▄▄▄▄▄▄▄           ▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄▄▄      ▐░▌          ▐░▌     ▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄█░▌               ▐░▌     ▐░▌ ▐░▌   ▐░▌▐░█▄▄▄▄▄▄▄▄▄      ▐░▌     ▐░█▄▄▄▄▄▄▄█░▌▐░▌          ▐░▌          ▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄█░▌\n▐░░░░░░░░░░░▌     ▐░▌     ▐░▌  ▐░▌  ▐░▌▐░░░░░░░░░░░▌          ▐░░░░░░░░░░▌ ▐░░░░░░░░░░░▌     ▐░▌          ▐░▌     ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌               ▐░▌     ▐░▌  ▐░▌  ▐░▌▐░░░░░░░░░░░▌     ▐░▌     ▐░░░░░░░░░░░▌▐░▌          ▐░▌          ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌\n▐░█▀▀▀▀▀▀▀▀▀      ▐░▌     ▐░▌   ▐░▌ ▐░▌ ▀▀▀▀▀▀▀▀▀█░▌          ▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀▀▀      ▐░▌          ▐░▌     ▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀█░█▀▀                ▐░▌     ▐░▌   ▐░▌ ▐░▌ ▀▀▀▀▀▀▀▀▀█░▌     ▐░▌     ▐░█▀▀▀▀▀▀▀█░▌▐░▌          ▐░▌          ▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀█░█▀▀ \n▐░▌               ▐░▌     ▐░▌    ▐░▌▐░▌          ▐░▌          ▐░▌       ▐░▌▐░▌               ▐░▌          ▐░▌     ▐░▌          ▐░▌     ▐░▌                 ▐░▌     ▐░▌    ▐░▌▐░▌          ▐░▌     ▐░▌     ▐░▌       ▐░▌▐░▌          ▐░▌          ▐░▌          ▐░▌     ▐░▌  \n▐░▌           ▄▄▄▄█░█▄▄▄▄ ▐░▌     ▐░▐░▌ ▄▄▄▄▄▄▄▄▄█░▌          ▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄▄▄      ▐░▌          ▐░▌     ▐░█▄▄▄▄▄▄▄▄▄ ▐░▌      ▐░▌            ▄▄▄▄█░█▄▄▄▄ ▐░▌     ▐░▐░▌ ▄▄▄▄▄▄▄▄▄█░▌     ▐░▌     ▐░▌       ▐░▌▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄▄▄ ▐░▌      ▐░▌\n ▐░▌          ▐░░░░░░░░░░░▌▐░▌      ▐░░▌▐░░░░░░░░░░░▌          ▐░░░░░░░░░░▌ ▐░░░░░░░░░░░▌     ▐░▌          ▐░▌     ▐░░░░░░░░░░░▌▐░▌       ▐░▌          ▐░░░░░░░░░░░▌▐░▌      ▐░░▌▐░░░░░░░░░░░▌     ▐░▌     ▐░▌       ▐░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌       ▐░▌\n ▀            ▀▀▀▀▀▀▀▀▀▀▀  ▀        ▀▀  ▀▀▀▀▀▀▀▀▀▀▀            ▀▀▀▀▀▀▀▀▀▀   ▀▀▀▀▀▀▀▀▀▀▀       ▀            ▀       ▀▀▀▀▀▀▀▀▀▀▀  ▀         ▀            ▀▀▀▀▀▀▀▀▀▀▀  ▀        ▀▀  ▀▀▀▀▀▀▀▀▀▀▀       ▀       ▀         ▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀         ▀ \n")

#UNVCLR Means universal clear. I use it a lot to clear the console for most screens. Taller screens with console full screen will still see some console output.
def unvclr():
    for i in range(1,25):
        print("\n\n")


def configassistant():

    # Welcome user
    time.sleep(2)
    unvclr()
    print("Hello. Welcome to config assistant.")
    time.sleep(1)
    unvclr()
    print("Warning..\nThis will skip some options and to get more personanilized information that you want in your config mnually change it in config.toml.\n\n")
    time.sleep(2)
    unvclr()
    print("Also this is in beta and may not work for the very LATEST release. Works fine as of 1/17/2023.")
    time.sleep(6)

    # Save more common stuff before user starts.
    fs = open("config.toml", "w")
    currentwrite = "[ai]\nai_similarity_enabled = false\nai_similarity_keywords = ""\n[settings]\nallow_nsfw = false\ntheme = dark\ntimes_to_run = 1\nopacity = 0.9"
    fs.write(currentwrite)

    time.sleep(1)
    unvclr()
    trston = input("How long would you like the transition between comments? (Ex. 0.2)\n")
    # Example string with this format: "You said 0.2 (newline) 0.2 Will be your transition time.
    print("You said " + trston + "\n" + trston + " Will be your transition time...")
    time.sleep(2)
    # Get credentials from user and save them to later save into the config file
    unvclr()
    print("Now get your credentils. This will be documented at shorturl.at/nzBUZ. Once you got them type anything in the console.")
    nothing = input("\nType something here when you have your credentials.\n")
    unvclr()
    print("Ready? Alright lets set them up!\n\n")
    clnt_id = input("Please enter your client ID credential.\n")
    print("Your input was " + clnt_id)
    time.sleep(1)
    clnt_secret = input("Please enter your client secret credential.\n")
    print("Your input was " + clnt_secret)
    time.sleep(1)
    user = input("Enter your username\n")
    print("Your input was " + user)
    time.sleep(1)
    passwrd = input("Enter your password\n")
    print("Your input was " + passwrd)
    time.sleep(1)
    print("Yay! I have gotten all of your credentials ready to be saved\nNow its time for your background choice. I will bring that up now.")
    time.sleep(2)
    unvclr()
    bkgrnd = input("Enter your background choice. Choices: minecraft,cluster-truck,gta,minecraft-2,csgo-surf,rocket-league,fall-guys.\n")
    print("Your input was " + bkgrnd)
    print("\nWarning: It will not display if the background is allowed. It will tell you it is wrong when you run it in main.py.")
    time.sleep(4)
    unvclr()
    print("Would you like to change the TTS settings or not? (Y/N)\n")
    confirmation = input("")
    if confirmation.capitalize() == "Y":
        tts = input("What would you like to set the tts voice to? \n")
        print("Your input was " + tts)
        time.sleep(1)
    else:
        print("Ok. I will set the TTS voice to fins default.")
        tts = "streamlabs_polly"
    print("All done! We are now creating the config with FS.\nPlease wait...")
    #Create config
    fs.close()
    fs = open("config.toml", 'a')
    fs.write("\ntransition = " + trston + "\nstorymode = false\nstorymodemethod = 1\nstorymode_max_length = 1000\nfps = 30\nresolution_w = 1080\nresolution_h = 1920\n\n[reddit.creds]\nclient_id = \"" + clnt_id + "\"\nclient_secret = \"" + clnt_secret + "\"\nusername = \"" + user + "\"\npassword = \"" + passwrd + "\"\n2fa = false\n\n[reddit.thread]\nrandom = false\nsubreddit = \"askreddit\"\npost_id = \"\"\nmax_commennt_length = 500\nmin_comment_length = 1\npost_lang = \"\"\nmin_comments = 15\n\n[settings.background]\nbackground_thumbnail = false\nbackground_thumbnail_font_family = \"arial\"\nbackground_thumbnail_font_size = 96\nbackground_thumbnail_font_color = \"255,255,255\"\n\n[settings.tts]\nvoice_choice = " + tts + "\naws_polly_voice = \"Matthew\"\nstreamlabs_polly_voice = \"Matthew\"\ntiktok_voice = \"\"\ntiktok_sessionid = \"\"\npython_voice = 1\npy_voicenum = \"\"\nsilence_duration = " + trston + "\nno_emojis = false\n\n*")
    print("Should be saved!")



#   _______  _______  ______   _______     _________ _______               _______  _______  _______
#  (  ____ \(  ___  )(  __  \ (  ____ \    \__   __/(  ____ \    |\     /|(  ____ \(  ____ )(  ____ \
#  | (    \/| (   ) || (  \  )| (    \/       ) (   | (    \/    | )   ( || (    \/| (    )|| (    \/
#  | |      | |   | || |   ) || (__           | |   | (_____     | (___) || (__    | (____)|| (__
#  | |      | |   | || |   | ||  __)          | |   (_____  )    |  ___  ||  __)   |     __)|  __)
#  | |      | |   | || |   ) || (             | |         ) |    | (   ) || (      | (\ (   | (
#  | (____/\| (___) || (__/  )| (____/\    ___) (___/\____) |    | )   ( || (____/\| ) \ \__| (____/\
#  (_______/(_______)(______/ (_______/    \_______/\_______)    |/     \|(_______/|/   \__/(_______/
#



# START CODE HERE
#Confirmation
print("Welcome to RedditVideoMakerBot Better Installer.\nAre you ready for it to run?")

confirmation = input("\n(Y/N)\n")
# Check if confirmation not == n/N
if not confirmation == "N":
    print("\nConfirmed!")
elif not confirmation == "n":
    print("\nConfirmed!")
else:
    print("Aborted.\nProgram will now quit.")
    quit("Aborted")
unvclr()
print("\n\n\nWARNING: What will happen soon is just it installing all of the python modules.")
time.sleep(3)
unvclr()

# Start installing python modules
# Used ChatGPT to get code to use the OS module for this


command = "pip3 install -r requirements.txt"
os.system(command)
time.sleep(1)
unvclr()



# Ending on installation
time.sleep(2)
unvclr()
print("\n\n\n\n\n\nInstallation with RedditVideoMakerBot should have been successful!\n\nCongrats!\n")
time.sleep(6)
configassistant()
endmsg()
time.sleep(10)
unvclr()
print("Have fun with RedditVideoMakerBot")
quit("Complete!")
