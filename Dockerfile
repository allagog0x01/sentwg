FROM golang:alpine3.7 AS deps

RUN apk add git gcc linux-headers make musl-dev wget
RUN go get -u github.com/golang/dep/cmd/dep && \
    mkdir -p /go/src/github.com/cosmos && \
    cd /go/src/github.com/cosmos && \
    git clone --depth 1 --branch develop https://github.com/sentinel-official/cosmos-sdk.git && \
    cd /go/src/github.com/cosmos/cosmos-sdk && \
    dep ensure -v && \
    make install
RUN cd /root && \
    wget https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py

FROM alpine:3.7

COPY --from=deps /go/bin/gaiacli /usr/local/bin/
COPY --from=deps /root/speedtest.py /usr/lib/python2.7/site-packages/

ADD sentinel /root/sentinel
ADD app.py run.sh config log_configuration.json /root/
RUN mkdir /root/.sentinel

ENV SENT_ENV=DEV

RUN echo '@testing http://nl.alpinelinux.org/alpine/edge/testing' >> /etc/apk/repositories && \
    apk update && \
    apk add --no-cache ca-certificates python mongodb wireguard-tools@testing && \
    mkdir -p /data/db && \
    wget -c https://bootstrap.pypa.io/get-pip.py -O /tmp/get-pip.py && \
    python /tmp/get-pip.py && \
    pip install --no-cache-dir falcon gunicorn pymongo requests configparser
RUN apk add --no-cache gcc python-dev musl-dev nano && \
    pip install --no-cache-dir ipython
RUN rm -rf /tmp/* /var/tmp/* /var/cache/apk/* /var/cache/distfiles/* /root/.cache .wget-hsts

CMD ["sh", "/root/run.sh"]
