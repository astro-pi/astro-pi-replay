#!/usr/bin/env bash

docker run -it --rm \
  -v "$(pwd)/rootfs/sys/class/graphics/fb1name:/sys/class/graphics/fb1name" \
  -v "$(pwd)/rootfs/dev/fb1:/dev/fb1" \
  foo:latest

