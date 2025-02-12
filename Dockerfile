ARG PYTHON_VERSION

FROM python:${PYTHON_VERSION}-slim AS builder
ARG NAME
ARG BIN_NAME
ARG VENV_NAME
ARG SKIP_DOWNLOAD
ENV NAME=${NAME}
ENV BIN_NAME=${BIN_NAME}
ENV VENV_NAME=${VENV_NAME}
ENV SKIP_DOWNLOAD=${SKIP_DOWNLOAD}

RUN apt update && apt-get install -y make libgl1 libglib2.0-0 libglx-mesa0

WORKDIR /opt/$NAME
RUN echo "${NAME} ${BIN_NAME} ${PYTHON_VERSION} ${VENV_NAME}" > foo
ADD Makefile .
ADD requirements.txt .
ADD requirements-dev.txt .
ADD pyproject.toml .
ADD MANIFEST.in .
ADD src src
RUN make clean && make install

RUN echo "#!/usr/bin/env bash" >> entrypoint.sh && \
    echo "/opt/${NAME}/${VENV_NAME}/bin/${BIN_NAME} \$*" >> entrypoint.sh && \
    chmod +x entrypoint.sh

RUN echo "source /opt/${NAME}/${VENV_NAME}/bin/activate" >> ~/.bashrc
RUN echo "source /opt/${NAME}/${VENV_NAME}/bin/activate" >> /etc/profile

ENV ASTRO_PI_REPLAY_REPLAY_DIR=/opt/astro_pi_replay/src/astro_pi_replay/resources/replay
RUN ln -s /opt/${NAME}/${VENV_NAME}/bin/Astro-Pi-Replay /usr/local/bin/Astro-Pi-Replay

ENTRYPOINT ["./entrypoint.sh"]
CMD ["--help"]
