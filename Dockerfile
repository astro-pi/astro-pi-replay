ARG PYTHON_VERSION

FROM python:${PYTHON_VERSION}-alpine as builder
ARG NAME
ARG BIN_NAME
ARG VENV_NAME
ENV NAME=${NAME}
ENV BIN_NAME=${BIN_NAME}
ENV VENV_NAME=${VENV_NAME}

RUN apk update && apk add make git gcc libc-dev libffi-dev
WORKDIR /opt/$NAME
RUN echo "${NAME} ${BIN_NAME} ${PYTHON_VERSION} ${VENV_NAME}" > foo
ADD Makefile .
ADD requirements.txt .
ADD requirements-dev.txt .
ADD pyproject.toml .
ADD MANIFEST.in .
ADD src src
RUN make clean && make install

ENTRYPOINT /opt/${NAME}/${VENV_NAME}/bin/${BIN_NAME}
