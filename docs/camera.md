# Camera specs

The Astro Pis have a High Quality Camera fitted with a CCTV lens.
For specific details (focal length, sensor dimensions, etc.) see:

  `src/astro_pi_executor/resources/OrbitAz/metadata.json`.

Taken with a ~10s delay in between each shot.

Code:

```python3
sense = SenseHat()
sense.color.gain = 60
sense.color.integration_cycles = 64
camera = PiCamera()
```

# Sensor modes

The Raspberry Pi High Quality Camera has 4 sensor modes (taken from https://github.com/raspberrypi/linux/blob/ac7c01535f9687c282c5a42a03264d9c659108a8/drivers/media/i2c/imx477.c#L480):

  1. mode_4056x3040 (12 mpix 10fps)
  2. mode_2028x1520 (2x2 binned. 40fps)
  3. mode_2028x1080 (1080p cropped mode)
  4. mode_1332x990 (4x4 binned. 120fps)

The `picamera` library selects the 'best' one based on the circumstances - combining
the framerate and any desired configuration (e.g. resolution).


Heuristics for which sensor mode is chosen:
  * The capture mode must be acceptable. All modes can be used for video recording, or for image captures from the video port (i.e. when use_video_port is True in calls to the various capture methods). Image captures when use_video_port is False must use an image mode (of which only two exist, both with the maximum resolution).
  * The closer the requested resolution is to the mode’s resolution the better, but downscaling from a higher sensor resolution to a lower output resolution is preferable to upscaling from a lower sensor resolution.
  * The requested framerate should be within the range of the sensor mode.
  * The closer the aspect ratio of the requested resolution to the mode’s resolution, the better. Attempts to set resolutions with aspect ratios other than 4:3 or 16:9 (which are the only ratios directly supported by the modes in the tables above) will choose the mode which maximizes the resulting field of view (FoV).



MMAL values are defined [here](https://github.com/raspberrypi/firmware/blob/8c8388c8de56fa72907a9370291753eb18fdd4bf/opt/vc/include/interface/mmal/mmal_parameters_camera.h).

# Ground sampling distance

This depends on the height / distance between the camera and the subject, as we

# Default values:

