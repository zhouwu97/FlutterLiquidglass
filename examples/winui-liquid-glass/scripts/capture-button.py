"""Verify a real held button, matched blur-only optics and native input.
Usage: python tools/LiquidGlassDemo/capture-button.py PID OUTPUT_DIRECTORY
"""
import ctypes
import json
import sys
import time
from pathlib import Path

import win32gui
import win32process
from PIL import ImageChops, ImageGrab, ImageStat
from pywinauto import Application

output = Path(sys.argv[2]).resolve()
output.mkdir(parents=True, exist_ok=True)
pid = int(sys.argv[1])
handles = []
win32gui.EnumWindows(lambda handle, _: handles.append(handle)
                     if win32gui.IsWindowVisible(handle)
                     and win32process.GetWindowThreadProcessId(handle)[1] == pid else None, None)
if len(handles) != 1:
    raise RuntimeError(f"Expected one demo window, found {handles}")
win32gui.ShowWindow(handles[0], 9)
window = Application(backend="uia").connect(process=pid).window(handle=handles[0])
window.set_focus()
time.sleep(.4)
user32 = ctypes.windll.user32
button = window.child_window(auto_id="AnchoredButton")
heading = window.child_window(auto_id="AnchoredHeading")
compare = window.child_window(auto_id="BlurOnly")
reduce = window.child_window(auto_id="ReduceMotion")
for checkbox in (compare, reduce):
    if checkbox.get_toggle_state():
        checkbox.toggle()
time.sleep(.6)
initial_heading = heading.rectangle()
records = []


def count():
    return int(button.window_text().rsplit(" ", 1)[-1])


def move(x, y, delay=.2):
    user32.mouse_event(0x8001, round(x * 65535 / (user32.GetSystemMetrics(0) - 1)),
                       round(y * 65535 / (user32.GetSystemMetrics(1) - 1)), 0, 0)
    time.sleep(delay)
    if max(abs(a - b) for a, b in zip(win32gui.GetCursorPos(), (x, y))) > 6:
        raise RuntimeError("Pointer input interrupted")


def down():
    user32.mouse_event(2, 0, 0, 0, 0)


def up():
    user32.mouse_event(4, 0, 0, 0, 0)


def capture(phase, held=False):
    if win32gui.GetForegroundWindow() != window.handle:
        raise RuntimeError("Demo is not the foreground window")
    if bool(user32.GetAsyncKeyState(1) & 0x8000) != held:
        raise RuntimeError("Unexpected native button state")
    if heading.rectangle() != initial_heading:
        raise RuntimeError("Child button press moved the parent card")
    left, top = win32gui.ClientToScreen(window.handle, (0, 0))
    client = win32gui.GetClientRect(window.handle)
    shot = ImageGrab.grab((left, top, left + client[2], top + client[3]), all_screens=True)
    shot.save(output / f"{phase}.png")
    rect = button.rectangle()
    records.append({"phase": phase, "held": held, "clicks": count(),
                    "bounds": [rect.left, rect.top, rect.right, rect.bottom]})
    return shot


rect = button.rectangle()
bx, by = (rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2
move(bx, by)
rest = capture("01-rest")
before = count()
try:
    down()
    time.sleep(.65)
    capture("02-held-glass", True)
    if count() != before:
        raise RuntimeError("Hold activated the button before release")
finally:
    up()
time.sleep(1)
capture("03-released")
if count() != before + 1:
    raise RuntimeError("Native release did not activate exactly once")

# A sibling UIA action can cancel native activation. Test comparison separately.
try:
    down()
    time.sleep(.65)
    glass = capture("04-held-comparison-glass", True)
    compare.toggle()
    time.sleep(.6)
    flat = capture("05-held-blur-only", True)
    compare.toggle()
    time.sleep(.6)
    capture("06-held-glass-again", True)
finally:
    up()
time.sleep(1)
capture("07-comparison-released")

# Compare the same stationary held pose. Optical expansion alone cannot pass this.
left, top = win32gui.ClientToScreen(window.handle, (0, 0))
dpi = user32.GetDpiForWindow(window.handle) / 96
region = (round(bx - left - 80 * dpi), round(by - top - 17 * dpi),
          round(bx - left + 80 * dpi), round(by - top + 17 * dpi))
optical_difference = sum(ImageStat.Stat(ImageChops.difference(glass.crop(region), flat.crop(region))).mean[:3]) / 3
if optical_difference < 2:
    raise RuntimeError(f"Native button shows no scene refraction: {optical_difference}")

before = count()
try:
    move(bx, by)
    down()
    move(bx + round(65 * dpi), by - round(20 * dpi), .4)
    capture("08-dragged", True)
finally:
    up()
time.sleep(.8)
if count() != before:
    raise RuntimeError("Button drag activated a click")

try:
    move(bx, by)
    down()
    time.sleep(.4)
    reduce.toggle()
    time.sleep(.5)
    capture("09-reduced-motion", True)
finally:
    up()
reduce.toggle()
time.sleep(.6)
before = count()
button.set_focus()
button.type_keys("{SPACE}")
time.sleep(.3)
if count() != before + 1:
    raise RuntimeError("Keyboard activation failed")
entry = window.child_window(auto_id="AnchoredEntry")
entry.set_focus()
entry.type_keys("native input", with_spaces=True)
entry.type_keys("^a")
entry.type_keys("replacement")
if entry.get_value() != "replacement":
    raise RuntimeError("Text editing or selection was intercepted")
entry.type_keys("^a{BACKSPACE}")
capture("10-settled")
result = {"input": "OS mouse events + UIA comparison setting + keyboard", "dpi": dpi,
          "optical_difference": optical_difference, "states": records,
          "native_release": True, "drag_suppressed": True, "keyboard": True, "editing_selection": True}
(output / "button.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result))
