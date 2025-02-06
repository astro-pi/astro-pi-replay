from orbit import ISS
from picamzero import Camera

iss = ISS()
cam = Camera()

pos = iss.coordinates()

cam.take_photo("photo_with_gps", 
   gps_coordinates=(pos.latitude.signed_dms(), pos.longitude.signed_dms())
)
