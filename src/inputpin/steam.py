import subprocess

# use steam app_id as the default because it contains the desktop preset
DESKTOP_APPID = 413080


def pin(appid: int) -> None:
    """
    Force Steam Input to use the controller config of appid.
    """
    subprocess.Popen(["steam", f"steam://forceinputappid/{appid}"])
