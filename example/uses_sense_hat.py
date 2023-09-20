from sense_hat import SenseHat
import os

sh = SenseHat()

"""
I am a big comment
with a little "string" inside
"""

headers = [
    "sh.get_accelerometer()",
    "sh.get_orientation_degrees()",
    "sh.get_accelerometer_raw()",
    "sh.get_orientation_radians()",
    "sh.get_compass()",
    "sh.get_compass_raw()",
    "sh.get_pixels()",
    "sh.get_gyroscope()",
    "sh.get_pressure()",
    "sh.get_gyroscope_raw()",
    "sh.get_temperature()",
    "sh.get_humidity()",
    "sh.get_temperature_from_humidity()",
    "sh.get_orientation()",
    "sh.get_temperature_from_pressure()",
]

data = [
    sh.get_accelerometer(),
    sh.get_orientation_degrees(),
    sh.get_accelerometer_raw(),
    sh.get_orientation_radians(),
    sh.get_compass(),
    sh.get_compass_raw(),
    sh.get_pixels(),
    sh.get_gyroscope(),
    sh.get_pressure(),
    sh.get_gyroscope_raw(),
    sh.get_temperature(),
    sh.get_humidity(),
    sh.get_temperature_from_humidity(),
    sh.get_orientation(),
    sh.get_temperature_from_pressure(),
]

with open("example.txt", "w") as f:
    for header, result in zip(headers, data):
        f.write(f"{header}: {str(result)}" + os.linesep)
