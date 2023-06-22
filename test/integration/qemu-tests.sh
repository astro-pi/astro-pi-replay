#!/usr/bin/env bash

# Constants

ARM=arm
AARCH64=aarch64
I836=i836
X86_64=x86_64
IMAGE_NAME=bullseye.img
COMPRESSION_TYPE=xz
OS_LITE_IMAGE=https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2023-05-03/2023-05-03-raspios-bullseye-armhf-lite.img.xz
OS_LITE_SHA256=67abd3bc034faf85b59b8e4a28982cb0ab1bc0504877ec3d426e05f6402ed225
OS_LITE_64_IMAGE=https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2023-05-03/2023-05-03-raspios-bullseye-arm64-lite.img.xz
OS_LITE_64_SHA256=bf982e56b0374712d93e185780d121e3f5c3d5e33052a95f72f9aed468d58fa7
QEMU_IMAGE_SIZE=8G

OS_I386_IMAGE=https://downloads.raspberrypi.org/rpd_x86/images/rpd_x86-2022-07-04/2022-07-01-raspios-bullseye-i386.iso
OS_I836_SHA256=5fa906df25e600bf7d7e6a5eb7b0e9b6605e60992ee6c8efe79bc99e7c2452bd

# Configuration
ARCH="$X86_64"

function test_dependencies_available() {
  # Checks that the required dependencies
  # to run the script successfully are
  # available.
  deps=(
    curl
    xz
    sha256sum
    "qemu-system-$ARCH"
  )
  failed=0
  for dependency in "${deps[@]}"; do
    type -P "$dependency" > /dev/null || <(failed=1 && echo "Failed finding '$dependency'")
  done
  if [ $failed -eq 1 ]; then echo "Woops"; exit 1; fi
}

function download_raspberry_pi_os() {
  local url="$OS_LITE_IMAGE"
  local expected_checksum="$OS_LITE_SHA256"
  if [ "$ARCH" = "$AARCH64" ]; then
    url="$OS_LITE_64_IMAGE"
    expected_checksum="$OS_LITE_64_SHA256"
  elif [ "$ARCH" = "$X86_64" ] || [ "$ARCH" = "$I863" ]; then
    url="$OS_I386_IMAGE"
    expected_checksum="$OS_I836_SHA256"
  fi
  curl -o "$IMAGE_NAME.$COMPRESSION_TYPE" "$url"
  actual_checksum=$(sha256sum "$IMAGE_NAME.$COMPRESSION_TYPE")
  if [ "$expected_checksum" != "$actual_checksum" ]; then
    echo "There was a problem downloading the Raspberry Pi OS"
    exit 1
  fi
  xz -d "$IMAGE_NAME.$COMPRESSION_TYPE"
}

function run_qemu() {
#
#  qemu-img resize "$IMAGE_NAME" "$QEMU_IMAGE_SIZE"
#
#  qemu-system-$ARCH --version \
#   -machine raspi3b \
#   -cpu cortex-a72 \
#   -dtb /mnt/test/bcm2710-rpi-3-b-plus.dtb \
#   -m 1G -smp 4 -serial stdio \
#   -kernel /mnt/test/kernel8.img \
#   -sd ./2022-04-04-raspios-bullseye-armhf.img \
#   -append "rw earlyprintk loglevel=8 console=ttyAMA0,115200 dwc_otg.lpm_enable=0 root=/dev/mmcblk0p2 rootdelay=1"

  qemu-system-$ARCH \
    -machine virt\
    -smp 8\
    -m 4G\
    -cpu cortex-a72 \
    -serial stdio \
    -bios /usr/share/edk2/aarch64/QEMU_EFI.fd \
    -drive if=none,file="$IMAGE_NAME",format=raw,id=hd  \
    -device qemu-xhci \
    -device usb-storage,drive=hd \
    -boot menu=on \
    -device VGA
    # -drive if=none,file=./fedora-coreos-36.20220806.3.0-metal.aarch64-resized.raw,format=raw,id=hd  \
}

echo "Chosen architecture: $ARCH"
test_dependencies_available
download_raspberry_pi_os
