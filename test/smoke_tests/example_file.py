from picamera import PiCamera
from sense_hat import SenseHat

cam = PiCamera()
cam.resolution = (4096, 2032)
sense = SenseHat()

for i in range(300):
    cam.capture("foo.png")
    humidity = sense.get_humidity()

    sense.get_temperature()
    sense.get_temperature_from_humidity()
    sense.get_temperature_from_pressure
    sense.get_pressure
    sense.get_orientation_radians
    sense.get_orientation_degrees
    sense.get_orientation
    sense.get_compass
    sense.get_compass_raw
    sense.get_gyroscope
    sense.get_gyroscope_raw
    sense.get_accelerometer
    sense.get_accelerometer_raw
    sense.colour.colour

    # This is necessarily ignored in data replay
    sense.set_imu_config() # is ignored

    # Similarly the below have no effect during data-replay:
    sense.colour.gain = 16
    sense.colour.integration_cycles = 4

    # And finally, there is no data for get_events()
    sense.get_events()


    # Additionally, the executor should manage the calls to...
    import skyfield
    # skyfield..

    # and...
    from orbit import ISS
