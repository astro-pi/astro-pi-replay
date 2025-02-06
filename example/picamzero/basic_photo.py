from picamzero import Camera
from pathlib import Path

current_dir = Path(__file__).parent

cam = Camera()
cam.take_photo("basic_photo.jpg")
