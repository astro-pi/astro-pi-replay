from sense_hat import SenseHat
sense = SenseHat()
mag_x = sense.get_compass_raw()["x"]
print(mag_x)
