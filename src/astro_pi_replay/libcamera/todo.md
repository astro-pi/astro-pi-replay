----------
To inspect
----------

ControlType,
Rectangle,
Size,
Orientation,
controls

StreamRole[StillCapture|Raw|VideoRecording|Viewfinder]
Request.Status.Complete
controls.draft.NoiseReductionModeEnum.[Minimal|HighQuality|Fast]
Size
PixelFormat
ColorSpace.Raw()
SensorConfiguration()
CameraConfiguration.Status.[Invalid|Adjusted]
_libcamera.[ColorSpace|Transform]

-----------
Inspections
-----------

>>> dir(libcamera)
['Camera', 'CameraConfiguration', 'CameraManager', 'ColorSpace', 'ControlId', 'ControlInfo', 'ControlType', 'FrameBuffer', 'FrameBufferAllocator', 'FrameMetadata', 'Orientation', 'PixelFormat', 'Point', 'Rectangle', 'Request', 'SensorConfiguration', 'Size', 'SizeRange', 'Stream', 'StreamConfiguration', 'StreamFormats', 'StreamRole', 'Transform', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__path__', '__spec__', '_libcamera', 'controls', 'formats', 'log_set_level', 'properties']

>>> libcamera.ControlType
<class 'libcamera._libcamera.ControlType'>
>>> dir(libcamera.ControlType)
['Bool', 'Byte', 'Float', 'Integer32', 'Integer64', 'Null', 'Rectangle', 'Size', 'String', '__class__', '__delattr__', '__dir__', '__doc__', '__entries', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__index__', '__init__', '__init_subclass__', '__int__', '__le__', '__lt__', '__members__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__', 'name', 'value']

>>> libcamera.Rectangle
<class 'libcamera._libcamera.Rectangle'>
>>> dir(libcamera.Rectangle)
['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'bounded_to', 'center', 'enclosed_in', 'height', 'is_null', 'scale_by', 'scaled_by', 'size', 'topLeft', 'translate_by', 'translated_by', 'width', 'x', 'y']

>>> libcamera.Size
<class 'libcamera._libcamera.Size'>
>>> dir(libcamera.Size)
['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__imul__', '__init__', '__init_subclass__', '__itruediv__', '__le__', '__lt__', '__module__', '__mul__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__truediv__', 'align_down_to', 'align_up_to', 'aligned_up_to', 'bound_to', 'bounded_to', 'bounded_to_aspect_ratio', 'centered_to', 'expand_to', 'expanded_to', 'expanded_to_aspect_ratio', 'grow_by', 'grown_by', 'height', 'is_null', 'shrink_by', 'shrunk_by', 'width']

>>> libcamera.Orientation
<class 'libcamera._libcamera.Orientation'>
>>> dir(libcamera.Orientation)
['Rotate0', 'Rotate0Mirror', 'Rotate180', 'Rotate180Mirror', 'Rotate270', 'Rotate270Mirror', 'Rotate90', 'Rotate90Mirror', '__class__', '__delattr__', '__dir__', '__doc__', '__entries', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__index__', '__init__', '__init_subclass__', '__int__', '__le__', '__lt__', '__members__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__', 'name', 'value']

>>> libcamera.StreamRole
<class 'libcamera._libcamera.StreamRole'>
>>> dir(libcamera.StreamRole)
['Raw', 'StillCapture', 'VideoRecording', 'Viewfinder', '__class__', '__delattr__', '__dir__', '__doc__', '__entries', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__index__', '__init__', '__init_subclass__', '__int__', '__le__', '__lt__', '__members__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__', 'name', 'value']

>>> libcamera.StreamRole.StillCapture
<StreamRole.StillCapture: 1>
>>> dir(libcamera.StreamRole.StillCapture)
['Raw', 'StillCapture', 'VideoRecording', 'Viewfinder', '__class__', '__delattr__', '__dir__', '__doc__', '__entries', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__index__', '__init__', '__init_subclass__', '__int__', '__le__', '__lt__', '__members__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__', 'name', 'value']
>>>

>>> libcamera.StreamRole.Raw
<StreamRole.Raw: 0>
>>> dir(libcamera.StreamRole.Raw)
['Raw', 'StillCapture', 'VideoRecording', 'Viewfinder', '__class__', '__delattr__', '__dir__', '__doc__', '__entries', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__index__', '__init__', '__init_subclass__', '__int__', '__le__', '__lt__', '__members__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__', 'name', 'value']
>>>

>>> libcamera.StreamRole.VideoRecording
<StreamRole.VideoRecording: 2>
>>> dir(libcamera.StreamRole.VideoRecording)
['Raw', 'StillCapture', 'VideoRecording', 'Viewfinder', '__class__', '__delattr__', '__dir__', '__doc__', '__entries', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__index__', '__init__', '__init_subclass__', '__int__', '__le__', '__lt__', '__members__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__', 'name', 'value']
>>>

>>> libcamera.StreamRole.Viewfinder
<StreamRole.Viewfinder: 3>
>>> dir(libcamera.StreamRole.Viewfinder)
['Raw', 'StillCapture', 'VideoRecording', 'Viewfinder', '__class__', '__delattr__', '__dir__', '__doc__', '__entries', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__index__', '__init__', '__init_subclass__', '__int__', '__le__', '__lt__', '__members__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__', 'name', 'value']

>>> libcamera.Request
<class 'libcamera._libcamera.Request'>
>>> dir(libcamera.Request)
['Reuse', 'Status', '__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'add_buffer', 'buffers', 'cookie', 'has_pending_buffers', 'metadata', 'reuse', 'sequence', 'set_control', 'status']

>>> libcamera.Request.Status
<class 'libcamera._libcamera.Request.Status'>
>>> libcamera.Request.Status

<class 'libcamera._libcamera.Request.Status'>
>>> dir(libcamera.Request.Status)
['Cancelled', 'Complete', 'Pending', '__class__', '__delattr__', '__dir__', '__doc__', '__entries', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__index__', '__init__', '__init_subclass__', '__int__', '__le__', '__lt__', '__members__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__', 'name', 'value']

>>> libcamera.Request.Status.Complete
<Status.Complete: 1>
>>> dir(libcamera.Request.Status.Complete)
['Cancelled', 'Complete', 'Pending', '__class__', '__delattr__', '__dir__', '__doc__', '__entries', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__index__', '__init__', '__init_subclass__', '__int__', '__le__', '__lt__', '__members__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__', 'name', 'value']

>>> libcamera.controls
<class 'libcamera._libcamera.controls'>
>>> dir(libcamera.controls)
['AeConstraintMode', 'AeConstraintModeEnum', 'AeEnable', 'AeExposureMode', 'AeExposureModeEnum', 'AeFlickerDetected', 'AeFlickerMode', 'AeFlickerModeEnum', 'AeFlickerPeriod', 'AeLocked', 'AeMeteringMode', 'AeMeteringModeEnum', 'AfMetering', 'AfMeteringEnum', 'AfMode', 'AfModeEnum', 'AfPause', 'AfPauseEnum', 'AfPauseState', 'AfPauseStateEnum', 'AfRange', 'AfRangeEnum', 'AfSpeed', 'AfSpeedEnum', 'AfState', 'AfStateEnum', 'AfTrigger', 'AfTriggerEnum', 'AfWindows', 'AnalogueGain', 'AwbEnable', 'AwbLocked', 'AwbMode', 'AwbModeEnum', 'Brightness', 'ColourCorrectionMatrix', 'ColourGains', 'ColourTemperature', 'Contrast', 'DigitalGain', 'ExposureTime', 'ExposureValue', 'FocusFoM', 'FrameDuration', 'FrameDurationLimits', 'HdrChannel', 'HdrChannelEnum', 'HdrMode', 'HdrModeEnum', 'LensPosition', 'Lux', 'Saturation', 'ScalerCrop', 'SensorBlackLevels', 'SensorTemperature', 'SensorTimestamp', 'Sharpness', '__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'draft', 'rpi']

>>> libcamera.controls.draft
<class 'libcamera._libcamera.controls.draft'>
>>> dir(libcamera.controls.draft)
['AePrecaptureTrigger', 'AePrecaptureTriggerEnum', 'AeState', 'AeStateEnum', 'AwbState', 'AwbStateEnum', 'ColorCorrectionAberrationMode', 'ColorCorrectionAberrationModeEnum', 'LensShadingMapMode', 'LensShadingMapModeEnum', 'MaxLatency', 'NoiseReductionMode', 'NoiseReductionModeEnum', 'PipelineDepth', 'SensorRollingShutterSkew', 'TestPatternMode', 'TestPatternModeEnum', '__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__']

>>> libcamera.controls.draft.NoiseReductionMode
libcamera.ControlId(10002, NoiseReductionMode, ControlType.Integer32)
>>> dir(libcamera.controls.draft.NoiseReductionMode)
['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'id', 'name', 'type']

>>> libcamera.controls.draft.NoiseReductionModeEnum
<class 'libcamera._libcamera.controls.draft.NoiseReductionModeEnum'>
>>> dir(libcamera.controls.draft.NoiseReductionModeEnum)
['Fast', 'HighQuality', 'Minimal', 'Off', 'ZSL', '__class__', '__delattr__', '__dir__', '__doc__', '__entries', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__index__', '__init__', '__init_subclass__', '__int__', '__le__', '__lt__', '__members__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__', 'name', 'value']

>>>
 >>> libcamera.controls.draft.NoiseReductionModeEnum.Minimal
<NoiseReductionModeEnum.Minimal: 3>
>>> dir(libcamera.controls.draft.NoiseReductionModeEnum.Minimal)
['Fast', 'HighQuality', 'Minimal', 'Off', 'ZSL', '__class__', '__delattr__', '__dir__', '__doc__', '__entries', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__index__', '__init__', '__init_subclass__', '__int__', '__le__', '__lt__', '__members__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__', 'name', 'value']

>>> libcamera.controls.draft.NoiseReductionModeEnum.HighQuality
<NoiseReductionModeEnum.HighQuality: 2>
(arg: 0) libcamera.controls.draft.NoiseReductionModeEnum.HighQuality
KeyboardInterrupt
>>> dir(libcamera.controls.draft.NoiseReductionModeEnum.HighQuality)
['Fast', 'HighQuality', 'Minimal', 'Off', 'ZSL', '__class__', '__delattr__', '__dir__', '__doc__', '__entries', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__index__', '__init__', '__init_subclass__', '__int__', '__le__', '__lt__', '__members__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__', 'name', 'value']
>>>

>>> libcamera.controls.draft.NoiseReductionModeEnum.Fast
<NoiseReductionModeEnum.Fast: 1>
>>> dir(libcamera.controls.draft.NoiseReductionModeEnum.Fast)
['Fast', 'HighQuality', 'Minimal', 'Off', 'ZSL', '__class__', '__delattr__', '__dir__', '__doc__', '__entries', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__index__', '__init__', '__init_subclass__', '__int__', '__le__', '__lt__', '__members__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__', 'name', 'value']
>>>


>>> libcamera.PixelFormat
<class 'libcamera._libcamera.PixelFormat'>
>>> dir(libcamera.PixelFormat)
['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'fourcc', 'modifier']

>>> libcamera.ColorSpace.Raw
<built-in method Raw of PyCapsule object at 0x7fa6f24150>
>>> dir(libcamera.ColorSpace.Raw)
['__call__', '__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__name__', '__ne__', '__new__', '__qualname__', '__reduce__', '__reduce_ex__', '__repr__', '__self__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__text_signature__']
>>>

>>> libcamera.SensorConfiguration
<class 'libcamera._libcamera.SensorConfiguration'>
>>> dir(libcamera.SensorConfiguration)
['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'analog_crop', 'binning', 'bit_depth', 'is_valid', 'output_size', 'skipping']
>>>

>>> libcamera.CameraConfiguration
<class 'libcamera._libcamera.CameraConfiguration'>
>>> dir(libcamera.CameraConfiguration)
['Status', '__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__iter__', '__le__', '__len__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'at', 'empty', 'orientation', 'sensor_config', 'size', 'validate']

>>> libcamera.CameraConfiguration.Status
<class 'libcamera._libcamera.CameraConfiguration.Status'>
>>> dir(libcamera.CameraConfiguration.Status)
['Adjusted', 'Invalid', 'Valid', '__class__', '__delattr__', '__dir__', '__doc__', '__entries', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__index__', '__init__', '__init_subclass__', '__int__', '__le__', '__lt__', '__members__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__', 'name', 'value']

>>> libcamera.CameraConfiguration.Status.Invalid
<Status.Invalid: 2>
>>> dir(libcamera.CameraConfiguration.Status.Invalid)
['Adjusted', 'Invalid', 'Valid', '__class__', '__delattr__', '__dir__', '__doc__', '__entries', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__index__', '__init__', '__init_subclass__', '__int__', '__le__', '__lt__', '__members__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__', 'name', 'value']
>>>

>>> libcamera.CameraConfiguration.Status.Adjusted
<Status.Adjusted: 1>
>>> dir(libcamera.CameraConfiguration.Status.Adjusted)
['Adjusted', 'Invalid', 'Valid', '__class__', '__delattr__', '__dir__', '__doc__', '__entries', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__index__', '__init__', '__init_subclass__', '__int__', '__le__', '__lt__', '__members__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__', 'name', 'value']


>>> libcamera.Transform
<class 'libcamera._libcamera.Transform'>
>>> dir(libcamera.Transform)
['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'compose', 'hflip', 'inverse', 'invert', 'transpose', 'vflip']

>>> libcamera.ColorSpace
<class 'libcamera._libcamera.ColorSpace'>
>>> dir(libcamera.ColorSpace)
['Primaries', 'Range', 'Raw', 'Rec2020', 'Rec709', 'Smpte170m', 'Srgb', 'Sycc', 'TransferFunction', 'YcbcrEncoding', '__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'primaries', 'range', 'transferFunction', 'ycbcrEncoding']

>>> libcamera.CameraManager
<class 'libcamera._libcamera.CameraManager'>
>>> dir(libcamera.CameraManager)
['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'cameras', 'event_fd', 'get', 'get_ready_requests', 'singleton', 'version']
>>>

>>> cms = libcamera.CameraManager.singleton()
[25:42:03.722429551] [2392]  INFO Camera camera_manager.cpp:284 libcamera v0.2.0+120-eb00c13d
[25:42:03.791480441] [2397]  WARN RPiSdn sdn.cpp:40 Using legacy SDN tuning - please consider moving SDN inside rpi.denoise
[25:42:03.793677372] [2397]  INFO RPI vc4.cpp:446 Registered camera /base/soc/i2c0mux/i2c@1/imx477@1a to Unicam device /dev/media3 and ISP device /dev/media0
>>> dir(cms)
['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'cameras', 'event_fd', 'get', 'get_ready_requests', 'singleton', 'version']
>>>

>>> cam
<libcamera._libcamera.Camera object at 0x7fba9ac470>
>>> dir(cam)
['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'acquire', 'configure', 'controls', 'create_request', 'generate_configuration', 'id', 'properties', 'queue_request', 'release', 'start', 'stop', 'streams']

>>> dir(cam.properties)
['__class__', '__class_getitem__', '__contains__', '__delattr__', '__delitem__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getitem__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__ior__', '__iter__', '__le__', '__len__', '__lt__', '__ne__', '__new__', '__or__', '__reduce__', '__reduce_ex__', '__repr__', '__reversed__', '__ror__', '__setattr__', '__setitem__', '__sizeof__', '__str__', '__subclasshook__', 'clear', 'copy', 'fromkeys', 'get', 'items', 'keys', 'pop', 'popitem', 'setdefault', 'update', 'values']
>>>

>>> cam.properties
{libcamera.ControlId(3, Model, ControlType.String): 'imx477', libcamera.ControlId(4, UnitCellSize, ControlType.Size): libcamera.Size(1550, 1550), libcamera.ControlId(10001, ColorFilterArrangement, ControlType.Integer32): 0, libcamera.ControlId(1, Location, ControlType.Integer32): 2, libcamera.ControlId(2, Rotation, ControlType.Integer32): 180, libcamera.ControlId(5, PixelArraySize, ControlType.Size): libcamera.Size(4056, 3040), libcamera.ControlId(7, PixelArrayActiveAreas, ControlType.Rectangle): (libcamera.Rectangle(8, 16, 4056, 3040),), libcamera.ControlId(8, ScalerCropMaximum, ControlType.Rectangle): libcamera.Rectangle(0, 0, 0, 0), libcamera.ControlId(10, SystemDevices, ControlType.Integer64): (20750, 20751, 20737, 20738, 20739)}

>>> cam.acquire()
>>> cam.configure(c)
[26:29:54.005771295] [2446]  INFO Camera camera.cpp:1183 configuring streams: (0) 800x600-XRGB8888
[26:29:54.006638643] [2450]  INFO RPI vc4.cpp:621 Sensor: /base/soc/i2c0mux/i2c@1/imx477@1a - Selected sensor format: 2028x1520-SBGGR12_1X12 - Selected unicam format: 2028x1520-pBCC
>>> cam.start()


>>> cam.create_request(0)
<libcamera._libcamera.Request object at 0x7fba98c230>
>>> r = cam.create_request(0)
>>> r
<libcamera._libcamera.Request object at 0x7fba9b3eb0>
>>>

>>> dir(r)
['Reuse', 'Status', '__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'add_buffer', 'buffers', 'cookie', 'has_pending_buffers', 'metadata', 'reuse', 'sequence', 'set_control', 'status']

>>> fb = libcamera.FrameBuffer.Plane()
>>> dir(fb)
['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'fd', 'length', 'offset']
>>> print(fb)
<libcamera._libcamera.FrameBuffer.Plane object at 0x7fbab968b0>
>>>

>>> c.at(0)
<libcamera._libcamera.StreamConfiguration object at 0x7fba9b22f0>

>>> sc = c.at(0)
>>> dir(sc)
['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'buffer_count', 'color_space', 'formats', 'frame_size', 'pixel_format', 'size', 'stream', 'stride']

>>> sc.stream
<libcamera._libcamera.Stream object at 0x7fba9b1df0>

>>> dir(sc.stream)
['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'configuration']

>>> sc.stream.configuration
<libcamera._libcamera.StreamConfiguration object at 0x7fba9c8b30>

>>> dir(sc.stream.configuration)
['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'buffer_count', 'color_space', 'formats', 'frame_size', 'pixel_format', 'size', 'stream', 'stride']
