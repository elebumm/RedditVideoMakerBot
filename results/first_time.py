import datetime
import json

format_data = "%Y-%m-%d %H:%M:%S.%f"
time = datetime.datetime.now().strftime(format_data)
print(time)

f = open("..\\video_creation\\data\\videos.json")

# loads videos.json into a dictionary
video_data = json.load(f)

for video in video_data:
    video["uploaded"] = False

# serialises the dictionary to json
json_obj = json.dumps(video_data, indent=4, default=str)
# writes the file
with open("..\\video_creation\\data\\videos.json", "w") as outfile:
    outfile.write(json_obj)
