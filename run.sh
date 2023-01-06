#!/bin/sh
docker run -v $(pwd)/out/:/app/assets -v $(pwd)/.env:/app/.env -v $(pwd)/results/:/app/results -it rvmt
