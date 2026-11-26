const SERVICE = "io.github.remnant_sys.InputPin";
const PATH = "/io/github/remnant_sys/InputPin";

function send(w) {
  if (w === null) {
    return;
  }
  // Steam tracks XWayland windows itself; they print as KWin::X11Window(0x...)
  const x11 = String(w).includes("X11Window");
  callDBus(SERVICE, PATH, SERVICE, "focus", w.pid, x11);
  console.info(
    "called dbus",
    JSON.stringify({ pid: w.pid, resource_class: w.resourceClass, x11: x11 }),
  );
}

// Steam's on-screen keyboard never takes focus, so windowActivated misses it.
// Matched by window type rather than caption, which Steam translates.
function isKeyboard(w) {
  return w.resourceClass === "steam" && w.utility && !w.wantsInput;
}

function keyboard(shown) {
  return function (w) {
    if (isKeyboard(w)) {
      callDBus(SERVICE, PATH, SERVICE, "keyboard", shown);
    }
  };
}

workspace.windowActivated.connect(send);
workspace.windowAdded.connect(keyboard(true));
workspace.windowRemoved.connect(keyboard(false));
send(workspace.activeWindow);
