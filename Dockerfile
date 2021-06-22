# FROM ethersphere/bee:0.6.2
FROM python:3.8.10

RUN mkdir -p /opt/data \
    && apt-get update \
    && apt-get install -y dnsutils \
    && wget https://github.com/ethersphere/bee/releases/download/v1.0.0/bee-linux-amd64 -O /usr/bin/bee \
    && chmod 755 /usr/bin/bee \
    && pip3 install websockets requests;

ADD py /opt/py

WORKDIR /opt
VOLUME /opt/data

EXPOSE 1633 1634 1635

CMD ["python3","-m","py.start"]