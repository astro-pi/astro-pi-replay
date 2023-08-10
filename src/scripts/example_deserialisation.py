import numpy as np


def test_rgb_raw():
    """
    Reads an rgb file saved with PiCamera.capture(file, format='rgb').
    This confirms that the bytes are serialised in row-major order.
    (or, in numpy parlance: C order).
    """

    with open("image1.rgb", "rb") as f:
        contents = f.read()

    resolution = (1280, 720)
    expected_img_shape = (*tuple(reversed(resolution)), 3)
    expected_bytes_count = np.prod(expected_img_shape)

    assert expected_bytes_count == len(contents)
    # Each number in the tuple is an 8bit number, hence dtype=np.uint8
    array = np.frombuffer(contents, dtype=np.uint8)
    assert len(array) == expected_bytes_count
    return array.reshape(expected_img_shape)


def test_rgba_raw():
    """
    Reads an rgba file saved with PiCamera.capture(file, format='rgba').
    This confirms that the bytes are serialised in row-major order.
    (or, in numpy parlance: C order).
    """
    with open("image1.rgba", "rb") as f:
        contents = f.read()
    resolution = (1280, 720)
    expected_img_shape = (*tuple(reversed(resolution)), 4)
    expected_bytes_count = np.prod(expected_img_shape)

    assert expected_bytes_count == len(contents)
    # Each number in the tuple is an 8bit number, hence dtype=np.uint8
    array = np.frombuffer(contents, dtype=np.uint8)
    assert len(array) == expected_bytes_count
    return array.reshape(expected_img_shape)


def test_yuv_raw():
    with open("image1.yuv", "rb") as f:
        contents = f.read()
    resolution = (1280, 720)
    num_pixels = np.prod(resolution)
    # YUV requires 6 bytes per 4 pixels, or 1.5 bytes per pixel!
    expected_bytes_count = round(np.prod(resolution) * 1.5)
    assert len(contents) == expected_bytes_count
    assert len(contents) % 6 == 0
    # Deserde is more involved
    # read 6 bytes at a time

    # Y'UV
    # All the Y' i values come first, followed by all the U values,
    # followed finally by all the V values.
    # There is a Y' value per pixel
    # The UV values are at quarter resolution, see:
    # https://en.wikipedia.org/wiki/YUV#Y%E2%80%B2UV420p_(and_Y%E2%80%B2V12_or_YV12)_to_RGB888_conversion

    # The horizontal resolution is rounded up to the nearest multiple of 32 pixels
    # The vertical resolution is rounded up to the nearest multiple of 16 pixels
    assert resolution[0] % 32 == 0
    assert resolution[1] % 16 == 0

    # Y is luminance
    y = np.frombuffer(contents[:num_pixels], dtype=np.uint8).reshape(
        (*tuple(reversed(resolution)), 1)
    )
    # UV are chrominance
    u = np.frombuffer(
        contents[num_pixels : int(num_pixels + (num_pixels / 4))], dtype=np.uint8
    )
    # .reshape((*tuple(reversed(resolution)), 1))
    v = np.frombuffer(contents[int(num_pixels + (num_pixels / 4)) :], dtype=np.uint8)
    # .reshape((*tuple(reversed(resolution)), 1))
    return y, u, v


# rgb = test_rgb_raw()
# im_rgb = Image.fromarray(rgb)
# im_rgb.save("rgb.jpg")
# rgba = test_rgba_raw()
# im_rgba = Image.fromarray(rgba)
# im_rgba.save("rgba.png")
y, u, v = test_yuv_raw()
