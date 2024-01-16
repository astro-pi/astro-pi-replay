ARG PYTHON_VERSION

FROM python:${PYTHON_VERSION}-slim as builder
ARG NAME
ARG BIN_NAME
ARG VENV_NAME
ARG SKIP_DOWNLOAD
ENV NAME=${NAME}
ENV BIN_NAME=${BIN_NAME}
ENV VENV_NAME=${VENV_NAME}
ENV SKIP_DOWNLOAD=${SKIP_DOWNLOAD}

RUN apt update && apt-get install -y make
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

RUN printenv >> env.txt

ENTRYPOINT ["./entrypoint.sh"]
CMD ["--help"]
