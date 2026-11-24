function send(w) {
  if (w === null) {
    return;
  }
  callDBus(
    "io.github.remnant_sys.InputPin",
    "/io/github/remnant_sys/InputPin",
    "io.github.remnant_sys.InputPin",
    "focus",
    w ? w.pid : 0,
  );
  console.info(
    "called dbus",
    JSON.stringify({ pid: w.pid, resource_class: w.resourceClass }),
  );
}

workspace.windowActivated.connect(send);
send(workspace.activeWindow);
