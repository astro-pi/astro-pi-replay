"""
Derived from:
    src/py/libcamera/py_helpers.cpp
"""
from .controls.controls import ControlType, ControlValue


def pyToControlValue(ob: object, type_: ControlType) -> ControlValue:
    if type_ == ControlType.Bool:
        return ControlValue(ob, type_)
    elif type_ == ControlType.Byte:
        #return controlValueMaybeArray<uint8_t>(ob);
        return ControlValue(ob, type_)
    elif type_ == ControlType.Integer32:
    	# return controlValueMaybeArray<int32_t>(ob);
        return ControlValue(ob, type_)
    elif type_ == ControlType.Integer64:
    	# return controlValueMaybeArray<int64_t>(ob);
        return ControlValue(ob, type_)
    elif type_ == ControlType.Float:
    	# return controlValueMaybeArray<float>(ob);
        return ControlValue(ob, type_)
    elif type_ == ControlType.String:
    	# return ControlValue(ob.cast<std::string>());
        return ControlValue(ob, type_)
    elif type_ == ControlType.Rectangle:
    	# return controlValueMaybeArray<Rectangle>(ob);
        return ControlValue(ob, type_)
    elif type_ == ControlType.Size:
    	# return ControlValue(ob.cast<Size>());
        return ControlValue(ob, type_)
    elif type_ == ControlType.Null:
        return ControlValue(None);
    else:
        raise RuntimeError("Control type not implemented")

