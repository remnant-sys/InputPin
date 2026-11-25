# inputpin

Makes Steam Input follow window focus on KDE Plasma Wayland.

Steam picks a controller config by watching the focused window, but it cannot see focus of
Wayland windows ([steam-for-linux#13314](https://github.com/ValveSoftware/steam-for-linux/issues/13314)),
so the controller stays on the Desktop Layout while a game runs. `inputpin` tracks focus itself
and pins the matching config.

## How it works

1. The KWin script `focus-relay` sends the active window's pid over the session D-Bus to
   `io.github.remnant_sys.InputPin`.
2. The service reads `SteamGameId` from `/proc/<pid>/environ`, which Steam sets for games and
   non-Steam shortcuts it launches.
3. It runs `steam steam://forceinputappid/<appid>`, or pins `413080` (Desktop Layout) when the
   window does not belong to a Steam-launched game. Steam's own window (`steamwebhelper`) gets
   `0` instead, so Steam picks the Big Picture or Desktop config itself.

On Ctrl-C it sends `steam://forceinputappid/0`, handing control back to Steam.

## Install

Requires KDE Plasma 6, native Steam (not Flatpak), uv, pipx and [Task](https://taskfile.dev)
(`go-task` on Fedora).

```sh
task install_script   # KWin script
task install          # service, via pipx
inputpin
```
