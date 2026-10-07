FROM python:3.12-alpine

RUN apk add --no-cache ffmpeg jq nodejs \
    && pip install --no-cache-dir \
    "yt-dlp[default]" \
    flask \
    flask-socketio \
    gevent \
    gevent-websocket

COPY app/ /app/
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
