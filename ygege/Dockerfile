# ARG doit être AVANT tous les FROM
ARG BUILD_FROM

# Stage 1: Builder ygege depuis les sources
FROM rust:alpine AS builder

RUN apk add --no-cache git musl-dev openssl-dev pkgconfig

WORKDIR /build
RUN git clone https://github.com/djerayane/ygege.git . && \
    git checkout develop && \
    cargo build --release

# Stage 2: Image finale avec base HA
FROM ${BUILD_FROM}

COPY --from=builder /build/target/release/ygege /app/ygege
COPY run.sh /
RUN chmod +x /run.sh /app/ygege

CMD [ "/run.sh" ]