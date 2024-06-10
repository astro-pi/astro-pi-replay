from typing import Optional


class CameraManager:
    _instance: Optional["CameraManager"] = None

    @staticmethod
    def singleton() -> "CameraManager":
        instance: "CameraManager"
        if CameraManager._instance is None:
            _instance = CameraManager()
            instance = _instance
        else:
            instance = CameraManager._instance
        return instance

    def cameras(self) -> dict:
        # TODO check with real implementation
        return {"id": 0, "Model": "IMX377", "Location": "", "Rotation": ""}
