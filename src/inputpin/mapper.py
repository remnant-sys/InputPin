import os
from pathlib import Path


def app_id(pid: int) -> int | None:
    """Steam appid of the game that owns pid, or None for anything Steam did not launch."""
    game_id = int(read_environ(pid).get("SteamGameId", 0))
    # A Steam game's id is its appid. A non-Steam shortcut's id is a 64-bit GameID
    # carrying the shortcut appid in its upper half.
    return (game_id >> 32 or game_id) or None


def is_steam_client(pid: int) -> bool:
    """Whether pid is the Steam client UI, which renders both the library and Big Picture."""
    try:
        return Path(f"/proc/{pid}/comm").read_text().strip() == "steamwebhelper"
    except OSError:  # the window's process already exited
        return False


def read_environ(pid: int) -> dict[str, str]:
    try:
        raw = Path(f"/proc/{pid}/environ").read_bytes()
    except OSError:  # the window's process already exited, or belongs to another user
        return {}
    return dict(
        entry.split("=", 1) for entry in os.fsdecode(raw).split("\0") if "=" in entry
    )
