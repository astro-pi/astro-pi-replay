#include <linux/uinput.h>
#include <linux/input.h>
#include <linux/module.h>
#include <linux/init.h>

static struct input_dev *input_dev;

static int __init vevdev_init(void)
{
    struct uinput_device_setup usetup;
    int err;

    // Allocate memory for the input device
    input_dev = input_allocate_device();
    if (!input_dev) {
        pr_err("Failed to allocate input device\n");
        return -ENOMEM;
    }

    // Enable the desired input events
    set_bit(EV_KEY, input_dev->evbit); // Enable key events

    set_bit(KEY_UP, input_dev->keybit); // Enable specific key (e.g., KEY_A)
    // Enable additional keys as needed

    // Set up the input device properties
    input_dev->name = "My Virtual Device"; // Replace with your desired device name
    input_dev->id.bustype = BUS_USB;
    input_dev->id.vendor = 0x1234; // Replace with your desired vendor ID
    input_dev->id.product = 0x5678; // Replace with your desired product ID

    // Register the input device
    err = input_register_device(input_dev);
    if (err) {
        pr_err("Failed to register input device: %d\n", err);
        input_free_device(input_dev);
        return err;
    }

    // Set up the uinput device properties
    memset(&usetup, 0, sizeof(usetup));
    strncpy(usetup.name, "My Virtual Device", UINPUT_MAX_NAME_SIZE);
    usetup.id.bustype = BUS_USB;
    usetup.id.vendor = 0x1234; // Replace with your desired vendor ID
    usetup.id.product = 0x5678; // Replace with your desired product ID

    // Create the uinput device
    err = uinput_create_user_dev(NULL, &usetup, &input_dev->dev);
    if (err) {
        pr_err("Failed to create uinput device: %d\n", err);
        input_unregister_device(input_dev);
        return err;
    }

    return 0;
}

static void __exit (void)
{
    // Destroy the uinput device
    uinput_destroy_user_dev(input_dev->dev);

    // Unregister and free the input device
    input_unregister_device(input_dev);
    input_free_device(input_dev);
}

module_init(vevdev_init);
module_exit(vevdev_exit);
