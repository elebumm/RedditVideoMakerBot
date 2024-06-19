import json
import re
from pathlib import Path

import toml
import tomlkit
from flask import flash


# Get validation checks from template
def get_checks():
    template = toml.load("utils/.config.template.toml")
    checks = {}

    def unpack_checks(obj: dict):
        for key in obj.keys():
            if "optional" in obj[key].keys():
                checks[key] = obj[key]
            else:
                unpack_checks(obj[key])

    unpack_checks(template)

    return checks


# Get current config (from config.toml) as dict
def get_config(obj: dict, done=None):
    if done is None:
        done = {}
    for key in obj.keys():
        if not isinstance(obj[key], dict):
            done[key] = obj[key]
        else:
            get_config(obj[key], done)

    return done


# Checks if value is valid
def check(value, checks):
    incorrect = False

    if value == "False":
        value = ""

    if not incorrect and "type" in checks:
        try:
            value = eval(checks["type"])(value)  # fixme remove eval
        except Exception:
            incorrect = True

    if (
        not incorrect and "options" in checks and value not in checks["options"]
    ):  # FAILSTATE Value isn't one of the options
        incorrect = True
    if (
        not incorrect
        and "regex" in checks
        and (
            (isinstance(value, str) and re.match(checks["regex"], value) is None)
            or not isinstance(value, str)
        )
    ):  # FAILSTATE Value doesn't match regular expression, or has regular expression but isn't a string.
        incorrect = True

    if (
        not incorrect
        and not hasattr(value, "__iter__")
        and (
            ("nmin" in checks and checks["nmin"] is not None and value < checks["nmin"])
            or ("nmax" in checks and checks["nmax"] is not None and value > checks["nmax"])
        )
    ):
        incorrect = True

    if (
        not incorrect
        and hasattr(value, "__iter__")
        and (
            ("nmin" in checks and checks["nmin"] is not None and len(value) < checks["nmin"])
            or ("nmax" in checks and checks["nmax"] is not None and len(value) > checks["nmax"])
        )
    ):
        incorrect = True

    if incorrect:
        return "Error"

    return value


# Modify settings (after the form is submitted)
def modify_settings(data: dict, config_load, checks: dict):
    # Modify config settings
    def modify_config(obj: dict, config_name: str, value: any):
        for key in obj.keys():
            if config_name == key:
                obj[key] = value
            elif not isinstance(obj[key], dict):
                continue
            else:
                modify_config(obj[key], config_name, value)

    # Remove empty/incorrect key-value pairs
    data = {key: value for key, value in data.items() if value and key in checks.keys()}

    # Validate values
    for name in data.keys():
        value = check(data[name], checks[name])

        # Value is invalid
        if value == "Error":
            flash("Some values were incorrect and didn't save!", "error")
        else:
            # Value is valid
            modify_config(config_load, name, value)

    # Save changes in config.toml
    with Path("config.toml").open("w") as toml_file:
        toml_file.write(tomlkit.dumps(config_load))

    flash("Settings saved!")

    return get_config(config_load)


# Delete background video
def delete_background(key):
    # Read backgrounds.json
    with open("utils/backgrounds.json", "r", encoding="utf-8") as backgrounds:
        data = json.load(backgrounds)

    # Remove background from backgrounds.json
    with open("utils/backgrounds.json", "w", encoding="utf-8") as backgrounds:
        if data.pop(key, None):
            json.dump(data, backgrounds, ensure_ascii=False, indent=4)
        else:
            flash("Couldn't find this background. Try refreshing the page.", "error")
            return

    # Remove background video from ".config.template.toml"
    config = tomlkit.loads(Path("utils/.config.template.toml").read_text())
    config["settings"]["background"]["background_choice"]["options"].remove(key)

    with Path("utils/.config.template.toml").open("w") as toml_file:
        toml_file.write(tomlkit.dumps(config))

    flash(f'Successfully removed "{key}" background!')


# Add background video
def add_background(youtube_uri, filename, citation, position):
    # Validate YouTube URI
    regex = re.compile(r"(?:\/|%3D|v=|vi=)([0-9A-z\-_]{11})(?:[%#?&]|$)").search(youtube_uri)

    if not regex:
        flash("YouTube URI is invalid!", "error")
        return

    youtube_uri = f"https://www.youtube.com/watch?v={regex.group(1)}"

    # Check if the position is valid
    if position == "" or position == "center":
        position = "center"

    elif position.isdecimal():
        position = int(position)

    else:
        flash('Position is invalid! It can be "center" or decimal number.', "error")
        return

    # Sanitize filename
    regex = re.compile(r"^([a-zA-Z0-9\s_-]{1,100})$").match(filename)

    if not regex:
        flash("Filename is invalid!", "error")
        return

    filename = filename.replace(" ", "_")

    # Check if the background doesn't already exist
    with open("utils/backgrounds.json", "r", encoding="utf-8") as backgrounds:
        data = json.load(backgrounds)

        # Check if key isn't already taken
        if filename in list(data.keys()):
            flash("Background video with this name already exist!", "error")
            return

        # Check if the YouTube URI isn't already used under different name
        if youtube_uri in [data[i][0] for i in list(data.keys())]:
            flash("Background video with this YouTube URI is already added!", "error")
            return

    # Add background video to json file
    with open("utils/backgrounds.json", "r+", encoding="utf-8") as backgrounds:
        data = json.load(backgrounds)

        data[filename] = [youtube_uri, filename + ".mp4", citation, position]
        backgrounds.seek(0)
        json.dump(data, backgrounds, ensure_ascii=False, indent=4)

    # Add background video to ".config.template.toml"
    config = tomlkit.loads(Path("utils/.config.template.toml").read_text())
    config["settings"]["background"]["background_choice"]["options"].append(filename)

    with Path("utils/.config.template.toml").open("w") as toml_file:
        toml_file.write(tomlkit.dumps(config))

    flash(f'Added "{citation}-{filename}.mp4" as a new background video!')

    return
