import httplib2
import os
import random
import sys
import time
import datetime
import json

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from datetime import timedelta
from datetime import datetime

# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (
    httplib2.HttpLib2Error,
    IOError,
)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google API Console at
# https://console.developers.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secrets.json"

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the API Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(
    os.path.join(os.path.dirname(__file__), CLIENT_SECRETS_FILE)
)

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def get_authenticated_service(args):
    # print(CLIENT_SECRETS_FILE)
    flow = flow_from_clientsecrets(
        CLIENT_SECRETS_FILE,
        scope=YOUTUBE_UPLOAD_SCOPE,
        message=MISSING_CLIENT_SECRETS_MESSAGE,
    )

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, args)

    return build(
        YOUTUBE_API_SERVICE_NAME,
        YOUTUBE_API_VERSION,
        http=credentials.authorize(httplib2.Http()),
    )


def initialize_upload(options, next_upload_time):
    args = argparser.parse_args()
    youtube = get_authenticated_service(args)
    tags = None
    if options["keywords"]:
        tags = options["keywords"].split(",")

    body = dict(
        snippet=dict(
            title=options["title"],
            description=options["description"],
            tags=tags,
            categoryId=options["category"],
        ),
        status=dict(
            privacyStatus=options["privacyStatus"],
            publishAt=options[
                "publishTime"
            ],  # might need to be publishedAt, implement this
        ),
    )

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(options["file"], chunksize=-1, resumable=True),
    )

    resumable_upload(insert_request, next_upload_time)


# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(insert_request, next_upload_time):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print("Uploading file...")
            status, response = insert_request.next_chunk()
            if response is not None:
                if "id" in response:
                    print(
                        "Video id {0} was successfully uploaded and will be published at {1}".format(
                            response["id"], next_upload_time
                        )
                    )
                    ## upload success
                    updateUploadedStatus(i, next_upload_time)

                else:
                    exit("The upload failed with an unexpected response: %s" % response)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (
                    e.resp.status,
                    e.content,
                )
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit("No longer attempting to retry.")

            max_sleep = 2**retry
            sleep_seconds = random.random() * max_sleep
            print("Sleeping %f seconds and then retrying...") % sleep_seconds
            time.sleep(sleep_seconds)


def updateUploadedStatus(currIndex, time):
    # opens the json containing video_creation data (used for logic and upload data)
    f = open("..\\video_creation\\data\\videos.json")
    # loads videos.json into a dictionary
    video_data = json.load(f)

    video_data[currIndex]["uploaded_at"] = time
    video_data[currIndex]["uploaded"] = True

    # serialises the dictionary to json
    json_obj = json.dumps(video_data, indent=4, default=str)
    # writes the file
    with open("..\\video_creation\\data\\videos.json", "w") as outfile:
        outfile.write(json_obj)


def upload_youtube(video, prev_video):
    format_data = "%Y-%m-%d %H:%M:%S"
    next_upload = datetime.strptime(prev_video["uploaded_at"], format_data) + timedelta(
        hours=4
    )
    file_name = video["subreddit"] + "/" + video["filename"]
    title = "r/" + video["subreddit"] + " : " + video["reddit_title"]
    description = (
        "r/"
        + video["subreddit"]
        + " | "
        + video["reddit_title"]
        + "?"
        + " 🔔 Hit the bell next to Subscribe so you never miss a video! ❤️ Like and Comment 🧍 Subscribe if you are new on the channel!"
    )

    if len(title) >= 99:
        title = title[0:96] + "..."

    if len(title) <= 99:
        title = title + "?"

    options = {
        "file": file_name,
        "title": title,
        "description": description,
        "category": "22",
        "keywords": "reddit,shorts,askReddit",
        "privacyStatus": "private",
        "publishTime": next_upload.isoformat(),
    }

    if not os.path.exists(options["file"]):
        # print(options["file"])
        exit(
            "could not find the specified file --> {0} / {1}".format(
                options["file"].split("/")[0], options["file"].split("/")[1]
            )
        )

    initialize_upload(options, next_upload)


if __name__ == "__main__":

    # opens the json containing video_creation data (used for logic and upload data)
    f = open("..\\video_creation\\data\\videos.json")
    # loads videos.json into a dictionary
    video_data = json.load(f)
    options = {}
    uploaded = 0
    for i, video in enumerate(video_data):
        if video["uploaded"] == False:
            if uploaded < 6:
                prev_video = list(video_data)[i - 1]
                try:
                    upload_youtube(video, prev_video)
                    video["uploaded_at"] = next_upload.strftime(format_data)
                    uploaded += 1

                except HttpError as e:
                    print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
