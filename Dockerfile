FROM python:3.8-slim-buster

WORKDIR ~/OSAM/Build_bot/bot_tele_girl

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "flickr_gaixinh_suutam.py"]