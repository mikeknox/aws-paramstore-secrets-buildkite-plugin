FROM python:3.7-alpine

RUN sed -i 's/http\:\/\/dl-cdn.alpinelinux.org/https\:\/\/alpine.global.ssl.fastly.net/g' /etc/apk/repositories \
    && apk --no-cache add gcc musl-dev libffi-dev openssl-dev \
    && pip3 install moto coverage

ADD . /plugin
WORKDIR /plugin

RUN pip3 install .

CMD python3 -m unittest