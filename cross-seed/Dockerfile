FROM node:20-alpine

RUN apk add --no-cache jq \
    && npm install -g cross-seed@6.13.7
    
COPY run.sh /
RUN chmod a+x /run.sh

ENTRYPOINT ["/bin/sh", "/run.sh"]
