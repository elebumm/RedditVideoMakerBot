#!/bin/sh
sudo docker run -v $(pwd)/video_creation/data:/app/video_creation/data -v $(pwd)/config.toml:/app/config.toml -v $(pwd)/out/:/app/assets -v $(pwd)/.env:/app/.env -v $(pwd)/results:/app/results -it rvmt

