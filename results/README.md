# Upload script

-   videos go into this results folder
-   script needs to be in the same directory as videos
-   videos scheduled to release every 4 hours

# Files needed

-   client_secrets.json

I have left a .template for you to copy

```
{
    "web": {
        "client_id": < your client id goes here >,
        "client_secret": < your client secret goes here >,
        "redirect_uris": [],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token"
    }
}


```

# Changes required

-   All objects in videos.json

```
{
    ...,
    "uploaded": false,
    "uploaded_at": "2022-10-20 12:00:00"
}
```

YYYY-MM-DD HH:MM:SS

you can get the uploaded_at time by running the first_time.py script and using the print output.
uploaded : false has been added to the videos.py payload so should be uploaded : false by defualt.

[Link to the docs](https://developers.google.com/youtube/v3/guides/uploading_a_video) I used to get this working.
