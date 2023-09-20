#!/usr/bin/env bash

DEBIAN=debian-12.0.0-arm64-netinst.iso
IMG=debian.qcow

if [ ! -f $DEBIAN ]; then
  wget https://cdimage.debian.org/cdimage/release/current/arm64/iso-cd/debian-12.0.0-arm64-netinst.iso
fi

if [ ! -f debian.qcow ]; then
  qemu-img create -f qcow2 $IMG  2G
fi

# https://cloud.debian.org/images/cloud/bullseye/latest/debian-11-genericcloud-arm64.qcow2

qemu-system-aarch64 \
  -M virt \
  -hda $IMG \
  -cdrom $DEBIAN \
  -boot d \
  -m 2G \
  -accel hvf \
  -bios edk2-aarch64-code.fd \
  -nographic \
  -cpu host

# TODO connect to the installation
