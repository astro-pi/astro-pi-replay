Schema for `data.csv`
---------------------

The `data.csv` files are read by the SenseHatAdapter class.
Each `data.csv` file in `resources/replay/VIS/*` has the following columns, created
by saving the output of the method:

| name | method |
| ---- | ------ |
| temp | `get_temperature()` |
| pres | `get_pressure()` |
| hum  | `get_humidity()` |
| red | `colour.colour[0]` |
| green | `colour.colour[1]` |
| blue | `colour.colour[2]` |
| clear | `colour.colour[3]` |
| yaw | `get_orientation()["yaw"]` |
| pitch | `get_orientation()["pitch"]` |
| roll | `get_orientation()["roll"]` |
| mag_x | `get_compass_raw()["x"]` |
| mag_y | `get_compass_raw()["y"]` |
| mag_z | `get_compass_raw()["z"]` |
| acc_x | `get_accelerometer_raw()["x"]` |
| acc_y | `get_accelerometer_raw()["y"]` |
| acc_z | `get_accelerometer_raw()["z"]` |
| gyro_x | `get_gyroscope_raw()["x"]` |
| gyro_y | `get_gyroscope_raw()["y"]` |
| gyro_z | `get_gyroscope_raw()["z"]` |
| datetime | `datetime.datetime.now()` |

The `capture_all.py` module in `src/scripts` collects a lot more data, which
will be incorporated into the SenseHatAdapter in future. Therefore, these column names
may change.
