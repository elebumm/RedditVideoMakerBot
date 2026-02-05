FROM python:3.10.14-slim

# system deps
RUN apt update && apt-get install -y \
    ffmpeg \
    python3-pip \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

# allow GUI
ENV DISPLAY=:0

# run GUI instead of CLI
CMD ["python3", "GUI.py"]
