import asyncio
import contextlib

from dbus_fast.aio import MessageBus
from dbus_fast.annotations import DBusInt32
from dbus_fast.service import ServiceInterface, method

from inputpin import mapper, steam

BUS_NAME = "io.github.remnant_sys.InputPin"
OBJECT_PATH = "/" + BUS_NAME.replace(".", "/")


class InputPin(ServiceInterface):
    def __init__(self):
        super().__init__(BUS_NAME)
        self._pinned: int | None = None

    @method()
    def focus(self, pid: DBusInt32):
        appid = mapper.app_id(pid) or steam.DESKTOP_APPID
        print("focused pid:", pid, "appid:", appid)
        # each pin spawns the steam launcher, avoid pinning within the same window
        if appid != self._pinned:
            steam.pin(appid)
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
