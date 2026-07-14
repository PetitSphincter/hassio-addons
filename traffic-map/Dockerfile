ARG BUILD_FROM
FROM $BUILD_FROM

# Installer Python et dépendances
RUN apk add --no-cache \
    python3 \
    py3-pip \
    && pip3 install --break-system-packages --no-cache-dir Pillow requests

# Copier le script
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
