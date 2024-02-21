class GPIOZeroError(Exception):
    pass


class DeviceClosed(GPIOZeroError):
    pass


class GPIODeviceError(GPIOZeroError):
    pass


class GPIODeviceClosed(GPIODeviceError, DeviceClosed):
    pass
