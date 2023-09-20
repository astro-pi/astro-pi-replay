from picamera import PiCamera

cam = PiCamera()

for i in range(3):
    print("Capturing")
    cam.capture(f"photo_{i}.jpg")
