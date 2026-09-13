FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive 

WORKDIR /winsdk

COPY prepare.sh /winsdk
COPY gen-setenv.py /winsdk

RUN cd /winsdk && \
    chmod +x ./prepare.sh && \
    ./prepare.sh
