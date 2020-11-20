FROM ubuntu:latest
MAINTAINER Zhihong Li <zhihongli@bennington.edu>

RUN apt-get update && apt-get install -y \
	curl \
	python-dev \
	python-setuptools \
	python3-pip \
	--no-install-recommends && \
	rm -rf /var/lib/apt/lists/* && \
	apt-get clean

RUN pip3 install --upgrade pip
RUN pip3 uninstall bson
RUN pip3 uninstall pymongo
RUN pip3 install flask
RUN pip3 install flask_pymongo


ADD . /SoundCloud-FullStack
WORKDIR /SoundCloud-FullStack

EXPOSE 5000

ENV FLASK_APP=main.py

CMD /usr/local/bin/flask run --host=0.0.0.0