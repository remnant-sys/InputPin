import asyncio
import contextlib

from dbus_fast.aio import MessageBus
from dbus_fast.annotations import DBusBool, DBusInt32
from dbus_fast.service import ServiceInterface, method

from inputpin import mapper, steam

BUS_NAME = "io.github.remnant_sys.InputPin"
OBJECT_PATH = "/" + BUS_NAME.replace(".", "/")


class InputPin(ServiceInterface):
    def __init__(self) -> None:
        super().__init__(BUS_NAME)
        self._pinned: int | None = None
        self._wanted = 0  # config the focused window should get
        self._keyboard = False
        self._focus_count = 0

    @method()
    async def focus(self, pid: DBusInt32, x11: DBusBool) -> None:
        self._focus_count += 1
        count = self._focus_count
        if mapper.is_steam_client(pid):
            big_picture = await steam.is_big_picture()
            # a newer focus arrived while xprop ran
            if count != self._focus_count:
                return
            # not 0: Steam takes 12-15 s to notice Big Picture regained focus
            self._wanted = (
                steam.BIG_PICTURE_APPID if big_picture else steam.DESKTOP_APPID
            )
        elif not (game := mapper.app_id(pid)):
            self._wanted = steam.DESKTOP_APPID
        elif x11 and mapper.has_steam_overlay(pid):
            # Steam tracks X11 games itself, a pin would block the Steam menu
            self._wanted = 0
        else:
            self._wanted = game
        print("focused pid:", pid, "appid:", self._wanted)
        self._apply()

    @method()
    def keyboard(self, shown: DBusBool) -> None:
        # Steam restores the controller after the keyboard only if nothing is pinned
        self._keyboard = shown
        self._apply()

    def _apply(self) -> None:
        appid = 0 if self._keyboard else self._wanted
        # each pin spawns the steam launcher, avoid pinning within the same window
        if appid == self._pinned:
            return

        if not steam.pin(appid):
            # a Steam started later is unpinned
            self._pinned = None
            return

        self._pinned = appid


async def serve():
    bus = await MessageBus().connect()
    bus.export(OBJECT_PATH, InputPin())
    await bus.request_name(BUS_NAME)
    print("watch started")
    await bus.wait_for_disconnect()


def main():
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(serve())
    print("exiting...")
    steam.pin(0)


if __name__ == "__main__":
    main()
