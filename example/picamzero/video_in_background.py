from picamzero import Camera
from time import sleep

cam = Camera()
cam.start_recording("background_video")
sleep(5)
cam.stop_recording()
