#!/usr/bin/env bash

sed -i "s/kkkm/test_data/g" worker-utils.js
sed -i "s/kkkm/test_data/g" worker-utils.umd.js
docker run -it --rm \
  --entrypoint /bin/sh \
  -v "$(pwd)/wheels":/wheels \
  replay-test

  # -v "$(pwd)/wheels":/opt/pyodide-tests/wheels \
