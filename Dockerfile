FROM python:3.7.12-alpine3.14
MAINTAINER Zhihong Li <zhihongli@bennington.edu>

RUN pip3 install --upgrade pip
RUN pip3 uninstall -y bson pymongo
RUN pip3 install flask flask_pymongo

ADD . /SoundCloud-FullStack
WORKDIR /SoundCloud-FullStack

EXPOSE 5000

ENTRYPOINT [ "python" ]

CMD ["main.py"]
