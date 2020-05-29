FROM python:3.7-alpine

ADD . /plugin

WORKDIR /plugin

RUN pip3 install .

CMD python3 -m unittest