"""Record real switch press/drag/reversal/release pixels with actual frame durations."""
import ctypes
import hashlib
import json
import sys
import time
from pathlib import Path

import win32gui
import win32process
from PIL import Image, ImageDraw, ImageFont, ImageGrab
from pywinauto import Application
from pywinauto.keyboard import send_keys

pid, output = int(sys.argv[1]), Path(sys.argv[2]).resolve()
toggle_id = next((a.split("=", 1)[1] for a in sys.argv[3:] if a.startswith("--toggle-id=")), "GlassToggle")
cancel = "--cancel" in sys.argv[3:]
tap = "--tap" in sys.argv[3:]
output.mkdir(parents=True, exist_ok=True)
handles = []
win32gui.EnumWindows(lambda h, _: handles.append(h) if win32gui.IsWindowVisible(h)
                     and win32process.GetWindowThreadProcessId(h)[1] == pid
                     and win32gui.GetClassName(h) == "WinUIDesktopWin32WindowClass" else None, None)
if len(handles) != 1:
    raise RuntimeError(f"Expected one demo window: {handles}")
win32gui.ShowWindow(handles[0], 9)
window = Application(backend="uia").connect(process=pid).window(handle=handles[0])
window.set_focus()
for name in ("BlurOnly", "ReduceMotion"):
    check = window.child_window(auto_id=name)
    if check.exists(timeout=.2) and check.get_toggle_state():
        check.toggle()
toggle = window.child_window(auto_id=toggle_id).wrapper_object()
if tap and toggle.iface_toggle.CurrentToggleState:
    toggle.iface_toggle.Toggle()
elif not tap and not toggle.iface_toggle.CurrentToggleState:
    if cancel:
        raise RuntimeError("Choose an already-on setting for the green-preserving cancellation check")
    toggle.iface_toggle.Toggle()
settings_arg = next((a.split("=", 1)[1] for a in sys.argv[3:] if a.startswith("--settings-file=")), None)
settings_path = Path(settings_arg) if settings_arg else None
settings_before = hashlib.sha256(settings_path.read_bytes()).hexdigest() if cancel and settings_path is not None and settings_path.exists() else None
window.set_focus()
time.sleep(.7)
user32 = ctypes.windll.user32
dpi = user32.GetDpiForWindow(window.handle) / 96
rect = toggle.rectangle()
left, right, cy = round(rect.left + 13 * dpi), round(rect.left + 35 * dpi), (rect.top + rect.bottom) // 2
box = (round(rect.left - 42 * dpi), round(rect.top - 25 * dpi),
       round(rect.right + 25 * dpi), round(rect.bottom + 25 * dpi))
frames, records = [], []
held = False
pointer = (right, cy)
started = time.perf_counter()


def move(x, y):
    global pointer
    pointer = (round(x), round(y))
    user32.mouse_event(0x8001, round(pointer[0] * 65535 / (user32.GetSystemMetrics(0) - 1)),
                       round(pointer[1] * 65535 / (user32.GetSystemMetrics(1) - 1)), 0, 0)


def frame(phase):
    if win32gui.GetForegroundWindow() != window.handle:
        raise RuntimeError("Demo lost foreground; discard this recording")
    if bool(user32.GetAsyncKeyState(1) & 0x8000) != held:
        raise RuntimeError("Native held state changed unexpectedly")
    if max(abs(a - b) for a, b in zip(win32gui.GetCursorPos(), pointer)) > 6:
        raise RuntimeError("Pointer input interrupted; discard this recording")
    shot = ImageGrab.grab(box, all_screens=True)
    frames.append(shot)
    records.append({"phase": phase, "seconds": time.perf_counter() - started, "pointer": pointer, "held": held})
    return shot


def sample(seconds, phase, start_x=None, end_x=None):
    start = time.perf_counter()
    while time.perf_counter() - start < seconds:
        tick = time.perf_counter()
        if start_x is not None:
            progress = min(1, (tick - start) / seconds)
            move(start_x + (end_x - start_x) * progress, cy)
        frame(phase)
        time.sleep(max(0, 1 / 50 - (time.perf_counter() - tick)))
    if end_x is not None:
        move(end_x, cy)


move(left if tap else right, cy)
time.sleep(.15)
sample(.15, "rest")
color = None
if tap:
    for direction, x, expected in (("forward", left, 1), ("backward", right, 0)):
        move(x, cy)
        try:
            user32.mouse_event(2, 0, 0, 0, 0)
            held = True
            sample(.045, direction + "-pointer-down")
            if toggle.iface_toggle.CurrentToggleState != 1 - expected:
                raise RuntimeError("A tap committed before pointer-up")
        finally:
            user32.mouse_event(4, 0, 0, 0, 0)
            held = False
        sample(1.35, direction + "-tap-lift-travel-release")
        if toggle.iface_toggle.CurrentToggleState != expected:
            raise RuntimeError("A tap did not toggle once on pointer-up")
else:
    try:
        user32.mouse_event(2, 0, 0, 0, 0)
        held = True
        sample(.45, "pressed")
        shot = frame("held-green")
        px = round(right + 3 * dpi - box[0])
        py = cy - box[1]
        color = shot.getpixel((px, py))
        if not (color[1] > 195 and color[0] < 90):
            raise RuntimeError(f"Pressed rail lost its saturated green: {color}")
        shot.save(output / "held-green.png")
        sample(.6, "slow-drag", right, left)
        sample(.15, "hold-left")
        sample(.08, "fast-right", left, right)
        sample(.08, "reverse-left", right, left)
        sample(.08, "reverse-right", left, right)
        if toggle.iface_toggle.CurrentToggleState != 1:
            raise RuntimeError("Dragging committed the semantic state before release")
        if cancel:
            send_keys("{ESC}")
    finally:
        user32.mouse_event(4, 0, 0, 0, 0)
        held = False
    sample(.9, "release-and-settle")
    if toggle.iface_toggle.CurrentToggleState != 1:
        raise RuntimeError("Release did not commit the final on position")
settings_unchanged = settings_before is None or hashlib.sha256(settings_path.read_bytes()).hexdigest() == settings_before
if not settings_unchanged:
    raise RuntimeError("Cancellation modified application settings")

# Display zoom only; native frame pixels and actual capture times remain available.
zoom = 3
font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 17)
display = []
for i, (shot, row) in enumerate(zip(frames, records)):
    shot.save(output / f"frame-{i:03d}.png")
    canvas = Image.new("RGB", (shot.width * zoom, shot.height * zoom + 30), "#f6f7fa")
    canvas.paste(shot.resize((shot.width * zoom, shot.height * zoom), Image.Resampling.NEAREST), (0, 30))
    ImageDraw.Draw(canvas).text((8, 3), row["phase"], font=font, fill="#263346")
    display.append(canvas)
durations = [max(10, round((records[i + 1]["seconds"] - row["seconds"]) * 1000))
             if i + 1 < len(records) else 250 for i, row in enumerate(records)]
display[0].save(output / "native-motion.gif", save_all=True, append_images=display[1:], duration=durations, loop=0)
result = {"input": "OS mouse events", "toggle_id": toggle_id, "dpi": dpi, "zoom": zoom, "crop": box,
          "held_green_rgb": color, "semantic_commit": "cancelled" if cancel else "release only", "tap": tap,
          "settings_unchanged": settings_unchanged, "frames": records}
(output / "motion.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps({"frames": len(frames), "seconds": records[-1]["seconds"], "held_green_rgb": color,
                  "gif": str(output / "native-motion.gif")}))
