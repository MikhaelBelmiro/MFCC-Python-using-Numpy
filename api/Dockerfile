FROM python:3.7.13

WORKDIR /api

RUN apt-get update -y 

RUN apt-get install -y ffmpeg libsndfile1

COPY ./requirements.txt ./

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . ./

EXPOSE 7071

CMD [ "python", "/api/main.py"]