# About

The European Astro Pi Challenge is an [ESA Education](https://www.esa.int/Education) project run in collaboration with the [Raspberry Pi Foundation](https://www.raspberrypi.org/).


# Picamera

The Basic Recipes are all supported, with a few caveats:
Supports the _public_ API of the PiCamera class as faithfully as possible.

- no yuv support (though could use Image.convert("YCbCr")
- no bayer support
- no custom encoders, etc.
# Bayer isn't supported - sorry (we just don't have the data).
# Also any deprecated method (as of vX) is also not supported.

Only the PiCamera class and the PiCamera Array classes are available.

# SenseHat

