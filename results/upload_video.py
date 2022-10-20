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


def initialize_upload(youtube, options, i, next_upload_time):
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

    resumable_upload(insert_request, i, next_upload_time)


# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(insert_request, i, next_upload_time):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print("Uploading file...")
            status, response = insert_request.next_chunk()
            if response is not None:
                if "id" in response:
                    print("Video id '%s' was successfully uploaded." % response["id"])
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

    # print(datetime.datetime.now().isoformat())
    # print(video_data[i - 1])
    # print(video_data[i])


if __name__ == "__main__":

    # opens the json containing video_creation data (used for logic and upload data)
    f = open("..\\video_creation\\data\\videos.json")
    # loads videos.json into a dictionary
    video_data = json.load(f)

    descriptionBeginning = "r/askReddit | "
    descriptionEnd = " 🔔 Hit the bell next to Subscribe so you never miss a video! ❤️ Like and Comment 🧍 Subscribe if you are new on the channel!"
    # reddit​ #redditstories​ #askreddit​ #shorts​
    titlebBeggining = "r/askReddit: "  # 13 characters

    options = {}
    uploaded = 0
    for i, video in enumerate(video_data):
        if video["uploaded"] == False:
            if uploaded < 2:
                prev_video = list(video_data)[i - 1]
                ############# 2022-10-19 16:39:46.887878
                format_data = "%Y-%m-%d %H:%M:%S"
                # print("prev_video", prev_video)
                # print("video", video)
                next_upload = datetime.strptime(
                    prev_video["uploaded_at"], format_data
                ) + timedelta(hours=4)
                # print(next_upload)
                titleEnding = "..."
                if len(video["reddit_title"]) < 84:
                    titleEnding = "?"
                    # print(len(video["reddit_title"]))

                options = {
                    "file": video["filename"],
                    "title": titlebBeggining
                    + video["reddit_title"][0:84]
                    + titleEnding,
                    "description": descriptionBeginning
                    + video["reddit_title"]
                    + descriptionEnd,
                    "category": "22",
                    "keywords": "reddit,shorts,askReddit",
                    "privacyStatus": "private",
                    "publishTime": next_upload.isoformat()
                    # June 19th, 2022 at 8:20 AM
                }

                args = argparser.parse_args()

                if not os.path.exists(options["file"]):
                    print(options["file"])
                    exit("Please specify a valid file using the --file= parameter ")

                youtube = get_authenticated_service(
                    args
                )  # args must be a new implementation of args object
                try:
                    initialize_upload(youtube, options, i, next_upload)
                    uploaded += 1
                    print(options["title"])
                    video["uploaded_at"] = next_upload.strftime(format_data)

                except HttpError as e:
                    print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
