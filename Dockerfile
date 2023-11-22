FROM python:3.10.9-slim

RUN apt update
RUN apt install ffmpeg python3-pip rubberband-cli espeak python3-pyaudio -y

RUN python3 -m pip install --upgrade pip

RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
RUN python3 -m spacy download en_core_web_sm

# tricks for pytube : https://github.com/elebumm/RedditVideoMakerBot/issues/142 
# (NOTE : This is no longer useful since pytube was removed from the dependencies)
# RUN sed -i 's/re.compile(r"^\\w+\\W")/re.compile(r"^\\$*\\w+\\W")/' /usr/local/lib/python3.8/dist-packages/pytube/cipher.py
RUN echo ZmluZCAvIC1wYXRoICcqL21vdmllcHkvdG9vbHMucHknIC1wcmludDAgfCB3aGlsZSByZWFkIC1kICQnXDAnIGZpbGU7IGRvCiAgc2VkIC1pIC1lICdzLyciJyInTW92aWVweSAtIFJ1bm5pbmc6XFxuPj4+ICIrICIgIi5qb2luKGNtZCknIiciJy8iTW92aWVweSAtIFJ1bm5pbmc6XFxuPj4+ICIgKyAiICIuam9pbihjbWQpL2cnICIkZmlsZSIKZG9uZQ== | base64 --decode | bash

ADD . /app

CMD ["python3", "main.py"]
