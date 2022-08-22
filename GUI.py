import json
import re
import webbrowser
from pathlib import Path

# Used "tomlkit" instead of "toml" because it doesn't change formatting on "dump"
import tomlkit
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)

# Set the hostname
HOST = "localhost"
# Set the port number
PORT = 4000

# Configure application
app = Flask(__name__, template_folder="GUI")

# Configure secret key only to use 'flash'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Display index.html
@app.route("/")
def index():
    return render_template("index.html")


# Make videos.json accessible
@app.route("/videos.json")
def videos_json():
    return send_from_directory("video_creation/data", "videos.json")


# Make videos in results folder accessible
@app.route("/results/<path:name>")
def results(name):
    return send_from_directory("results", name, as_attachment=True)


@app.route("/add_background", methods=["POST"])
def add_background():
    # Get form values
    youtube_uri = request.form.get("youtube_uri").strip()
    filename = request.form.get("filename").strip()
    citation = request.form.get("citation").strip()
    position = request.form.get("position").strip()

    # Validate YouTube URI
    regex = re.compile(
        r"(?:\/|%3D|v=|vi=)([0-9A-z-_]{11})(?:[%#?&]|$)"
    ).search(youtube_uri)

    if not regex:
        flash("YouTube URI is invalid!", "error")
        return redirect(url_for("index"))

    youtube_uri = f"https://www.youtube.com/watch?v={regex.group(1)}"

    # Check if position is valid
    if position == "" or position == "center":
        position = "center"

    elif position.isdecimal():
        position = int(position)

    else:
        flash('Position is invalid! It can be "center" or decimal number.', "error")
        return redirect(url_for("index"))

    # Sanitize filename
    filename = filename.replace(" ", "-").split(".")[0]

    # Check if background doesn't already exist
    with open("utils/backgrounds.json", "r", encoding="utf-8") as backgrounds:
        data = json.load(backgrounds)

        # Check if key isn't already taken
        if filename in list(data.keys()):
            flash("Background video with this name already exist!", "error")
            return redirect(url_for("index"))

        # Check if the YouTube URI isn't already used under different name
        if youtube_uri in [data[i][0] for i in list(data.keys())]:
            flash("Background video with this YouTube URI is already added!", "error")
            return redirect(url_for("index"))

    # Add background video to json file
    with open("utils/backgrounds.json", "r+", encoding="utf-8") as backgrounds:
        data = json.load(backgrounds)

        data[filename] = [youtube_uri, filename + ".mp4", citation, position]
        backgrounds.seek(0)
        json.dump(data, backgrounds, ensure_ascii=False, indent=4)

    # Add background video to ".config.template.toml" to make it accessible
    config = tomlkit.loads(Path("utils/.config.template.toml").read_text())
    config["settings"]["background"]["background_choice"]["options"].append(filename)

    with Path("utils/.config.template.toml").open("w") as toml_file:
        toml_file.write(tomlkit.dumps(config))

    flash(f'Added "{citation}-{filename}.mp4" as a new background video!')

    return redirect(url_for("index"))


# Run browser and start the app
if __name__ == "__main__":
    webbrowser.open(f"http://{HOST}:{PORT}", new=2)
    print("Website opened in new tab. Refresh if it didn't load.")
    app.run(port=PORT)
