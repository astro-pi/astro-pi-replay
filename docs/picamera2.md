# Design Decision

One option would have been to try and compile libcamera into Emscripten, to avoid having to include stubs for each. However, unfortunately, libcamera relies on mechanisms (e.g. `eventfd` that are not supported by Emscripten).

Without investing substantial effort (leaving aside the fact that this would effectively rewrite most of the library) into creating a fork that replaces these elements with a POSIX alternative, this is not an option (although, it would be great if it were possible!).

libcamera also provides its own threading implementation, which relies on Linux  syscalls, etc.,

If this were possible, of course one could stub libcamera to return the next data, but this is not an option.

For this reason, the Picamera2 implementation makes no reference to libcamera,
and therefore the implementation deviates substantially from the real `picamera2` library.  Attemting to access the camera manager etc., will result in an error.
