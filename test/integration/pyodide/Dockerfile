FROM node:22.11.0-alpine

WORKDIR /opt/pyodide-tests

RUN npm install pyodide@0.26.1

# TODO Fetch the latest changes from the R3 bucket e.g.
# https://astro-pi-replay-online-static.astro-pi.org/releases/v0.4/worker-utils.js
COPY worker-utils*.js .

# It is expected that script.js is created/loaded in via a volume.
ENTRYPOINT ["node", "script.js"]


# The container env should set VITE__ASTRO_PI_REPLAY_INSTALL_URL
# to install the custom wheel.
# TODO Set ASTRO_PI_REPLAY_INSTALL_URL to install the custom wheel:
#   /wheels/astro-pi-replay-XXXX
