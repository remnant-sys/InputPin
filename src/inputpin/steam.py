import asyncio
import os
import subprocess
from pathlib import Path

# use steam app_id as the default because it contains the desktop preset
DESKTOP_APPID = 413080
# the config Steam itself activates for the Big Picture UI
BIG_PICTURE_APPID = 769
STEAM_DIR = Path.home() / ".steam"


def pin(appid: int) -> bool:
    """
    Force Steam Input to use the controller config of appid.
    Returns False without pinning while Steam is closed, as the launcher would start it.
    """
    if not is_running():
        return False
    subprocess.Popen(["steam", f"steam://forceinputappid/{appid}"])
    return True


def is_running() -> bool:
    # same check as is_steam_running() in steam.sh: steam.pid stays behind after exit,
    # so the pid must also hold steam.pipe open to rule out a recycled pid
    pipe = str(STEAM_DIR / "steam.pipe")
    try:
        pid = (STEAM_DIR / "steam.pid").read_text().strip()
        return any(os.readlink(fd) == pipe for fd in Path(f"/proc/{pid}/fd").iterdir())
    except OSError:  # no pid file, or the process exited
        return False


async def is_big_picture() -> bool:
    """Whether the active X11 window is Steam's Big Picture UI."""
    # KWin scripts can't read X11 properties or window ids
    active = await _xprop("-root", "_NET_ACTIVE_WINDOW")
    if "window id #" not in active:  # no X display, or no active window
        return False
    window = active.split()[-1]  # "_NET_ACTIVE_WINDOW(WINDOW): window id # 0x3600146"
    # set on Big Picture, not the library, and unlike the title not translated
    focus = await _xprop("-id", window, "STEAM_INPUT_FOCUS")
    return focus.startswith("STEAM_INPUT_FOCUS(")


async def _xprop(*args: str) -> str:
    process = await asyncio.create_subprocess_exec(
        "xprop",
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
    )
    out, _ = await process.communicate()
    return out.decode()
