#include <linux/module.h>
#include <linux/init.h>
#include <linux/uinput.h>

/* #include <linux/module.h> */
/* #include <linux/kernel.h> */
/* #include <linux/errno.h> */
/* #include <linux/string.h> */
/* #include <linux/mm.h> */
/* #include <linux/vmalloc.h> */
/* #include <linux/delay.h> */
/* #include <linux/interrupt.h> */
/* #include <linux/platform_device.h> */

/* #include <linux/fb.h> */

static int fd;
static bool fd_created = false;

static int __init vevdev_init(void) {
  struct uinput_setup usetup;

  fd = open("/dev/uinput", O_WRONLY | O_NONBLOCK);
  fd_created = true;

  /*
   * The ioctls below will enable the device that is about to be
   * created, to pass key events, in this case the space key.
   */
  ioctl(fd, UI_SET_EVBIT, EV_KEY);
  ioctl(fd, UI_SET_KEYBIT, KEY_UP);
  ioctl(fd, UI_SET_KEYBIT, KEY_DOWN);
  ioctl(fd, UI_SET_KEYBIT, KEY_LEFT);
  ioctl(fd, UI_SET_KEYBIT, KEY_RIGHT);
  ioctl(fd, UI_SET_KEYBIT, KEY_ENTER);

  // Fill the allocated memory with zeros
  memset(&usetup, 0, sizeof(usetup));
  usetup.id.bustype = BUS_USB;
  usetup.id.vendor = 0x1234; /* sample vendor */
  usetup.id.product = 0x5678; /* sample product */
  strcpy(usetup.name, "Raspberry Pi Sense HAT Joystick");

  ioctl(fd, UI_DEV_SETUP, &usetup);
  ioctl(fd, UI_DEV_CREATE);

  return 0;
}

static void __exit vevdev_exit(void) {

  if (fd_created) {
    ioctl(fd, UI_DEV_DESTROY);
    close(fd);
  }

  return 0;

}

module_init(vevdev_init);
module_exit(vevdev_exit);
