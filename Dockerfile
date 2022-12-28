FROM ubuntu:jammy

RUN apt-get update -qy && apt-get install -qy wget curl git jq bash vim nano python3 python3-pip && apt-get clean -qy

VOLUME /app
WORKDIR /app

COPY . /app

RUN cd /app && pip3 install -U -r requirements.txt

ENTRYPOINT [ "/app/bin/openaliaspy" ]