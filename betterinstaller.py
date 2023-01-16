
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
    print("Thanks for using betterinstaller! Hopefully this worked fine! Goodbye! -Fin-Github")
    print(" ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄        ▄  ▄▄▄▄▄▄▄▄▄▄▄            ▄▄▄▄▄▄▄▄▄▄   ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄            ▄▄▄▄▄▄▄▄▄▄▄  ▄▄        ▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄            ▄            ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄\n▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░▌      ▐░▌▐░░░░░░░░░░░▌          ▐░░░░░░░░░░▌ ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌          ▐░░░░░░░░░░░▌▐░░▌      ▐░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌          ▐░▌          ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌\n▐░█▀▀▀▀▀▀▀▀▀  ▀▀▀▀█░█▀▀▀▀ ▐░▌░▌     ▐░▌▐░█▀▀▀▀▀▀▀▀▀           ▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀▀▀  ▀▀▀▀█░█▀▀▀▀  ▀▀▀▀█░█▀▀▀▀ ▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌           ▀▀▀▀█░█▀▀▀▀ ▐░▌░▌     ▐░▌▐░█▀▀▀▀▀▀▀▀▀  ▀▀▀▀█░█▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌▐░▌          ▐░▌          ▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌\n▐░▌               ▐░▌     ▐░▌▐░▌    ▐░▌▐░▌                    ▐░▌       ▐░▌▐░▌               ▐░▌          ▐░▌     ▐░▌          ▐░▌       ▐░▌               ▐░▌     ▐░▌▐░▌    ▐░▌▐░▌               ▐░▌     ▐░▌       ▐░▌▐░▌          ▐░▌          ▐░▌          ▐░▌       ▐░▌\n▐░█▄▄▄▄▄▄▄▄▄      ▐░▌     ▐░▌ ▐░▌   ▐░▌▐░█▄▄▄▄▄▄▄▄▄           ▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄▄▄      ▐░▌          ▐░▌     ▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄█░▌               ▐░▌     ▐░▌ ▐░▌   ▐░▌▐░█▄▄▄▄▄▄▄▄▄      ▐░▌     ▐░█▄▄▄▄▄▄▄█░▌▐░▌          ▐░▌          ▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄█░▌\n▐░░░░░░░░░░░▌     ▐░▌     ▐░▌  ▐░▌  ▐░▌▐░░░░░░░░░░░▌          ▐░░░░░░░░░░▌ ▐░░░░░░░░░░░▌     ▐░▌          ▐░▌     ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌               ▐░▌     ▐░▌  ▐░▌  ▐░▌▐░░░░░░░░░░░▌     ▐░▌     ▐░░░░░░░░░░░▌▐░▌          ▐░▌          ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌\n▐░█▀▀▀▀▀▀▀▀▀      ▐░▌     ▐░▌   ▐░▌ ▐░▌ ▀▀▀▀▀▀▀▀▀█░▌          ▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀▀▀      ▐░▌          ▐░▌     ▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀█░█▀▀                ▐░▌     ▐░▌   ▐░▌ ▐░▌ ▀▀▀▀▀▀▀▀▀█░▌     ▐░▌     ▐░█▀▀▀▀▀▀▀█░▌▐░▌          ▐░▌          ▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀█░█▀▀ \n▐░▌               ▐░▌     ▐░▌    ▐░▌▐░▌          ▐░▌          ▐░▌       ▐░▌▐░▌               ▐░▌          ▐░▌     ▐░▌          ▐░▌     ▐░▌                 ▐░▌     ▐░▌    ▐░▌▐░▌          ▐░▌     ▐░▌     ▐░▌       ▐░▌▐░▌          ▐░▌          ▐░▌          ▐░▌     ▐░▌  \n▐░▌           ▄▄▄▄█░█▄▄▄▄ ▐░▌     ▐░▐░▌ ▄▄▄▄▄▄▄▄▄█░▌          ▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄▄▄      ▐░▌          ▐░▌     ▐░█▄▄▄▄▄▄▄▄▄ ▐░▌      ▐░▌            ▄▄▄▄█░█▄▄▄▄ ▐░▌     ▐░▐░▌ ▄▄▄▄▄▄▄▄▄█░▌     ▐░▌     ▐░▌       ▐░▌▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄▄▄ ▐░▌      ▐░▌\n ▐░▌          ▐░░░░░░░░░░░▌▐░▌      ▐░░▌▐░░░░░░░░░░░▌          ▐░░░░░░░░░░▌ ▐░░░░░░░░░░░▌     ▐░▌          ▐░▌     ▐░░░░░░░░░░░▌▐░▌       ▐░▌          ▐░░░░░░░░░░░▌▐░▌      ▐░░▌▐░░░░░░░░░░░▌     ▐░▌     ▐░▌       ▐░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌       ▐░▌\n ▀            ▀▀▀▀▀▀▀▀▀▀▀  ▀        ▀▀  ▀▀▀▀▀▀▀▀▀▀▀            ▀▀▀▀▀▀▀▀▀▀   ▀▀▀▀▀▀▀▀▀▀▀       ▀            ▀       ▀▀▀▀▀▀▀▀▀▀▀  ▀         ▀            ▀▀▀▀▀▀▀▀▀▀▀  ▀        ▀▀  ▀▀▀▀▀▀▀▀▀▀▀       ▀       ▀         ▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀         ▀ \n")


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
print("WARNING: What will happen soon is just it installing all of the python modules.\n It is not hacking your computer if you really think it is lol.")
time.sleep(3)

# Start installing python modules
# Used ChatGPT to get code to use the OS module for this

# Run a command to list the files in the current directory
command = "pip3 install -r requirements.txt"
os.system(command)
print("If no error is returned it should have worked!\nIt is recommended to run the installation for playwright just to make sure all is well.\n Running in 3 seconds.")
time.sleep(3)
print("Installing playwright")
time.sleep(1)
runcmd("pip install -r requirements.txt")
runcmd("python -m playwright install")
time.sleep(1)
runcmd("python -m playwright install-deps")


# Ending on installation
print("\n\n\n\n\n\nInstallation with playwright should have been successful!\n\nCongrats!\n\nSadly, I have not yet made a way to ask config details here.\n So you will have to adjust your config manually.")
time.sleep(6)


# Propmt if wanting to open config website.
print("\n\nWould you like me to open the page for config adjustments here?")
confirmation = input("\n (Y/N)\n")

# Handle input
if not confirmation == "N":
    print("\nConfirmed!")
elif not confirmation == "n":
    print("\nConfirmed!")
else:
    endmsg()

# Opening website
print("Opening")
time.sleep(2)
import webbrowser

# Open the website
webbrowser.open("reddit-video-maker-bot.netlify.app/docs/configuring")
endmsg()