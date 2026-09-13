FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

RUN test -d /usr/share/man/man1 || mkdir -p /usr/share/man/man1

RUN apt update && \
    apt install -y wget rclone socat nano curl git python3 python3.12-venv

RUN python3 -m venv fdroidserver-env && \
    . fdroidserver-env/bin/activate && \
    pip install git+https://gitlab.com/fdroid/fdroidserver.git
