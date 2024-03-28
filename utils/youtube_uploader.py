from simple_youtube_api.Channel import Channel
from simple_youtube_api.LocalVideo import LocalVideo

from video_data_generation import gemini


# logging into the channel
channel = Channel()
channel.login("./utils/client_secret.json", "./utils/credentials.storage")

def upload_video_to_youtube(video_path, data, thumbnail):
    # setting up the video that is going to be uploaded
    video = LocalVideo(file_path=video_path)

    # setting snippet
    video.set_title(data['title'])
    video.set_description(data["description"])
    tags = data["tags"].split(', ')
    if len(tags) == 1: tags = tags[0].split(',')
    video.set_tags(tags)
    # video.set_category("gaming")
    video.set_default_language("en-US")

    # setting status
    video.set_embeddable(True)
    video.set_license("youtube")
    video.set_privacy_status("public")
    video.set_public_stats_viewable(True)

    # setting thumbnail
    if thumbnail is not None: video.set_thumbnail_path(thumbnail)

    # uploading video and printing the results
    video = channel.upload_video(video)
    print(video.id)
    print(video)