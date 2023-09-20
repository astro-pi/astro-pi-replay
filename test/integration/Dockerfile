FROM debian:bullseye

ARG CHROOT_DIR=/opt/chroot

# Install debootstrap
# and create a chroot at /opt/chroot
RUN apt-get update && apt-get install -y debootstrap
RUN mkdir -p ${CHROOT_DIR} && debootstrap bullseye ${CHROOT_DIR} http://deb.debian.org/debian

# Emulate just enough of a fb device for the Sense Hat lib to start
RUN mkdir -p ${CHROOT_DIR}/sys/class/graphics/fb1 && echo "RPi-Sense FB" > ${CHROOT_DIR}/sys/class/graphics/fb1/name

# Emulate some directories for linux kernel changes so
# that the sense-hat and picamera libs are installed
RUN mkdir -p ${CHROOT_DIR}/etc/modprobe.d && touch ${CHROOT_DIR}/etc/modules

# Update the apt sources configuration
RUN mkdir -p ${CHROOT_DIR}/etc/apt/sources.list.d && echo "deb https://internal_repo:aak1aS3u@extranet.raspberrypi.org/internal_repo/ bullseye main" >> ${CHROOT_DIR}/etc/apt/sources.list && \
  echo "deb http://archive.raspberrypi.org/debian/ bullseye main" >> ${CHROOT_DIR}/etc/apt/sources.list.d/raspi.list

## Install the GPG key
RUN apt-get update && apt-get install -y curl && \
  curl -o raspberrypi-archive-keyring.deb https://archive.raspberrypi.org/debian/pool/main/r/raspberrypi-archive-keyring/raspberrypi-archive-keyring_2021.1.1+rpt1_all.deb && \
  mv raspberrypi-archive-keyring.deb ${CHROOT_DIR} && \
  chroot ${CHROOT_DIR} dpkg -i raspberrypi-archive-keyring.deb && rm ${CHROOT_DIR}/raspberrypi-archive-keyring.deb


# Install dependencies into the chroot
RUN chroot ${CHROOT_DIR} apt-get update && chroot ${CHROOT_DIR} apt-get install -y python3
# RUN apt-get install -y libraspberrypi0 libraspberrypi-dev libraspberrypi-doc libraspberrypi-bin

RUN chroot ${CHROOT_DIR} apt-get update && chroot ${CHROOT_DIR} apt-get install -y sense-hat
#python3-picamera


# Devices needed by sensehat
RUN mkdir -p ${CHROOT_DIR}/dev/fb1
RUN mkdir -p ${CHROOT_DIR}/dev/i2c0
RUN mkdir -p ${CHROOT_DIR}/sys/class/input/event1/device && echo "Raspberry Pi Sense HAT Joystick" > ${CHROOT_DIR}/sys/class/input/event1/device/name
RUN mkdir -p ${CHROOT_DIR}/dev/input && touch ${CHROOT_DIR}/dev/input/event1

COPY RTIMULib.ini ${CHROOT_DIR}/etc/RTIMULib.ini
