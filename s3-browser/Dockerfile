FROM python:3.12-alpine

RUN apk add --no-cache jq ca-certificates openssl \
    && pip install --no-cache-dir \
    boto3 \
    flask \
    humanize

COPY app/ /app/
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
