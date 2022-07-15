# Supported Background. Can add/remove background video here....
# <key>-<value> : key -> used as keyword for TOML file. value -> background configuration
# Format (value):
# 1. Youtube URI
# 2. filename
# 3. Citation (owner of the video)
# 4. Position of image clips in the background. See moviepy reference for more information. (https://zulko.github.io/moviepy/ref/VideoClip/VideoClip.html#moviepy.video.VideoClip.VideoClip.set_position)
background_options = {
    "motor-gta": (  # Motor-GTA Racing
        "https://www.youtube.com/watch?v=vw5L4xCPy9Q",
        "bike-parkour-gta.mp4",
        "Achy Gaming",
        lambda t: ("center", 480 + t),
    ),
    "rocket-league": (  # Rocket League
        "https://www.youtube.com/watch?v=2X9QGY__0II",
        "rocket_league.mp4",
        "Orbital Gameplay",
        lambda t: ("center", 200 + t),
    ),
    "minecraft": (  # Minecraft parkour
        "https://www.youtube.com/watch?v=n_Dv4JMiwK8",
        "parkour.mp4",
        "bbswitzer",
        "center",
    ),
    "gta": (  # GTA Stunt Race
        "https://www.youtube.com/watch?v=qGa9kWREOnE",
        "gta-stunt-race.mp4",
        "Achy Gaming",
        lambda t: ("center", 480 + t),
    ),
    "csgo-surf": (  # CSGO Surf
        "https://www.youtube.com/watch?v=E-8JlyO59Io",
        "csgo-surf.mp4",
        "Aki",
        "center",
    ),
    "cluster-truck": (  # Cluster Truck Gameplay
        "https://www.youtube.com/watch?v=uVKxtdMgJVU",
        "cluster_truck.mp4",
        "No Copyright Gameplay",
        lambda t: ("center", 480 + t),
    ),
}
