FROM python:3.11.5
RUN apt update && apt upgrade -y

LABEL authors="SoNicItconsulting"

RUN pip install --upgrade pip

WORKDIR /app
COPY  . /app
COPY requirements.txt /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "-u", "mpd_gui.py"]