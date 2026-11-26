import os
from pathlib import Path


def app_id(pid: int) -> int | None:
    """Steam appid of the game owning pid, or None if Steam did not launch it."""
    game_id = int(read_environ(pid).get("SteamGameId", 0))
    # shortcuts carry their appid in the upper half of a 64-bit GameID
    return (game_id >> 32 or game_id) or None


def is_steam_client(pid: int) -> bool:
    """Whether pid is the Steam client UI (library and Big Picture)."""
    try:
        return Path(f"/proc/{pid}/comm").read_text().strip() == "steamwebhelper"
    except OSError:  # the window's process already exited
        return False


def has_steam_overlay(pid: int) -> bool:
    """Whether Steam's in-game overlay library is loaded into pid."""
    try:
        return b"gameoverlayrenderer" in Path(f"/proc/{pid}/maps").read_bytes()
    except OSError:  # the window's process already exited
        return False


def steam_overlay_hooked(pid: int) -> bool:
    """Whether Steam's in-game overlay hooked into pid."""
    # Steam preloads gameoverlayrenderer.so into every game, even with the overlay off,
    # but starts "gameoverlayui -pid <pid>" only once the overlay hooked in
    target = f"-pid\0{pid}\0".encode()
    for proc in Path("/proc").glob("[0-9]*"):
        try:
            if (proc / "comm").read_text() == "gameoverlayui\n" and target in (
                proc / "cmdline"
            ).read_bytes():
                return True
        except OSError:  # the process already exited
            continue
    return False


def read_environ(pid: int) -> dict[str, str]:
    try:
        raw = Path(f"/proc/{pid}/environ").read_bytes()
    except OSError:  # the window's process already exited, or belongs to another user
        return {}
    return dict(
        entry.split("=", 1) for entry in os.fsdecode(raw).split("\0") if "=" in entry
    )
