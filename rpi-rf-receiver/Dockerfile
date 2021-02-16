ARG BUILD_FROM=ghcr.io/hassio-addons/base-python/amd64:6.0.0
FROM ${BUILD_FROM}

# Copy root filesystem
# COPY rootfs /

RUN apk add --no-cache coreutils wget nano \
        jq \
        clang \
        libgcc \
        libgc++ \
        gcc-gnat \
        g++ \
        make \
        libffi-dev \
        openssl-dev \
        mosquitto \
        mosquitto-dev \
        mosquitto-libs \
        mosquitto-clients \
        python3 \
        python3-dev
RUN pip3 install -U pip
RUN pip3 install -U virtualenv

# Copy data for add-on
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]

# Build arguments
ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_REF
ARG BUILD_VERSION

# Labels
LABEL \
    io.hass.name="RF Receiver" \
    io.hass.description="433 MHz RF Receiver" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    maintainer="" \
    org.opencontainers.image.title="RF Receiver" \
    org.opencontainers.image.description="433 MHz RF Receiver" \
    org.opencontainers.image.vendor="" \
    org.opencontainers.image.authors="" \
    org.opencontainers.image.licenses="MIT" \
    org.opencontainers.image.url="" \
    org.opencontainers.image.source="https://github.com/psallandre/hassio-addons" \
    org.opencontainers.image.documentation="https://github.com/psallandre/hassio-addons/blob/master/README.md" \
    org.opencontainers.image.created=${BUILD_DATE} \
    org.opencontainers.image.revision=${BUILD_REF} \
    org.opencontainers.image.version=${BUILD_VERSION}
