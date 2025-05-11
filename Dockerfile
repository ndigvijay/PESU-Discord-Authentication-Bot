# This Dockerfile runs Python and MongoDB in the same container

# docker build -t <image_name> .
# docker run --name <container_name> -t -i -d -p 27017:27017 <image_name>
# docker exec -it <container_name> bash
# mongod --logpath /var/log/mongodb/mongod.log
# python3 boot/bot.py &

FROM ubuntu:22.04

RUN apt update -y && apt upgrade -y
RUN apt install build-essential curl gnupg nano telnet software-properties-common -y

# Add deadsnakes PPA for Python 3.10 installation
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt update -y
RUN apt install python3.10 python3.10-distutils python3.10-dev -y

# Install pip for Python 3.10
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10

# MongoDB setup
RUN curl -fsSL https://pgp.mongodb.com/server-7.0.asc | \
   gpg -o /etc/apt/trusted.gpg.d/mongodb-server-7.0.gpg \
   --dearmor

RUN echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list

ARG DEBIAN_FRONTEND=noninteractive
RUN apt update -y
RUN apt install mongodb-org -y

COPY bot /bot
COPY requirements.txt /requirements.txt
COPY config.yml /config.yml

# Install requirements using Python 3.10
RUN python3.10 -m pip install -r requirements.txt

EXPOSE 27017
RUN mkdir -p /data/db
RUN chmod -R 777 /data/db

ENTRYPOINT ["/bin/bash"]