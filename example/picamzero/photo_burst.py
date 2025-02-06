from picamzero import Camera

cam = Camera()
cam.capture_sequence("seq", interval=1, num_images=10)
