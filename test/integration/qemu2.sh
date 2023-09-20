#!/usr/bin/env bash
#https://cloud.debian.org/images/cloud/bullseye/latest/debian-11-nocloud-arm64.qcow2

qemu-system-aarch64 \
  -M virt \
  -cpu host \
  -m 2G \
  -accel hvf \
  -bios edk2-aarch64-code.fd \
  -drive if=none,file=debian-11-nocloud-arm64.qcow2,id=hd0 \
  -device virtio-blk-device,drive=hd0 \
  -device e1000,netdev=net0 -netdev user,id=net0,hostfwd=tcp:127.0.0.1:5555-:22 \
  -nographic



  #-M virt \
  #-hda $IMG \
  #-cdrom $DEBIAN \
  #-boot d \

#######################
# virtual i2c device
#######################
# TODO connect to the installation
#
# apt-get install linux-headers-$(uname -r) i2c-tools build-essential
#
#
# wget https://raw.githubusercontent.com/torvalds/linux/master/drivers/i2c/i2c-stub.c
#
# echo "obj-m += i2c-stub.o\n all:\n\t make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules\n\nclean:\n\tmake -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean\n\n" > Makefile
#
#make
#insmod i2c-stub chip_addr=0x20
#root@debian:~# insmod i2c-stub.ko chip_addr=0x29,0x39,
#try: 0x1c,0x46,0x5c,0x5f,0x6a
#i2cdetect -y 0
#rmmod i2c_stub

#######################
# virtual frame buffer:
#######################
#
# https://github.com/torvalds/linux/blob/1ef6663a587ba3e57dc5065a477db1c64481eedd/drivers/video/fbdev/vfb.c (make sure to use the correct git tag that matches $(uname -r))
# modify the virtual buffer name from Virtual FB to RPi-Sense FB
# sed 's/"Virtual FB"/"RPi-Sense FB"/g' vfb.c

# insmod vfb vfb_enable=1
#

#######################
# virtual event device
#######################
# evemu or vinput looks quite interesting
# looking to mock /sys/class/input/event
# https://stackoverflow.com/questions/53639022/faking-an-input-device-for-testing-purpose
#
# uinput vs libevdev
