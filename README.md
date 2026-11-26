# inputpin

Makes Steam Input follow window focus on KDE Plasma Wayland.

Steam picks a controller config by watching the focused window, but it cannot see focus of
Wayland windows ([steam-for-linux#13314](https://github.com/ValveSoftware/steam-for-linux/issues/13314)),
so the controller stays on the Desktop Layout while a game runs. `inputpin` tracks focus itself
and pins the matching config.

## How it works

1. The KWin script `focus-relay` sends the active window's pid and whether it is an X11
   window over the session D-Bus to `io.github.remnant_sys.InputPin`.
2. The service reads `SteamGameId` from `/proc/<pid>/environ`, which Steam sets for games and
   non-Steam shortcuts it launches.
3. It runs `steam steam://forceinputappid/<appid>`, or pins `413080` (Desktop Layout) when the
   window does not belong to a Steam-launched game. Steam's own windows (`steamwebhelper`) get
   `769` for Big Picture, recognised by the `STEAM_INPUT_FOCUS` X11 property, and `413080`
   otherwise. X11 games with the Steam overlay loaded get `0`, since Steam follows their focus
   itself and a pin would block the Steam menu.
4. While Steam's on-screen keyboard is open, the pin is lifted (`0`), and it is restored when
   the keyboard closes.

On Ctrl-C it sends `steam://forceinputappid/0`, handing control back to Steam.

## Install

Requires KDE Plasma 6, native Steam (not Flatpak), `xprop`, uv, pipx and [Task](https://taskfile.dev)
(`go-task` on Fedora).

```sh
task install_script   # KWin script
task install          # service, via pipx
inputpin
```
