"""Capture real mouse input in an unlocked Windows session: pip install pywinauto pillow.

Usage: python scripts/capture-pointer.py PID OUTPUT_DIRECTORY
Only operates on the given demo process; screenshots contain its client area.
"""
import ctypes
import json
import sys
import time
from pathlib import Path

import win32gui
from PIL import Image, ImageGrab, ImageChops, ImageStat
from pywinauto import Application

pid, output = int(sys.argv[1]), Path(sys.argv[2]).resolve()
output.mkdir(parents=True, exist_ok=True)
window = Application(backend='uia').connect(process=pid).top_window()
window.set_focus()
heading = window.child_window(auto_id='AnchoredHeading')
initial = str(heading.rectangle())
h = heading.rectangle()
start = (int((h.left+h.right)/2), h.top-16)
records = []
started = time.perf_counter()
client_origin = win32gui.ClientToScreen(window.handle, (0, 0))
padding = round(20 * ctypes.windll.user32.GetDpiForWindow(window.handle) / 96)
edge_y = h.top - padding - client_origin[1]
edge_x = (h.left + h.right)//2 - client_origin[0]

def capture(phase, held=False, expected=None):
    if win32gui.GetForegroundWindow() != window.handle:
        raise RuntimeError('Demo is not foreground; do not use a locked or obscured desktop as evidence.')
    down = bool(ctypes.windll.user32.GetAsyncKeyState(1) & 0x8000)
    if held != down:
        raise RuntimeError(f'Unexpected mouse state during {phase}; another input may have interrupted the trace.')
    position=win32gui.GetCursorPos()
    if expected and max(abs(position[i]-expected[i]) for i in (0,1))>2:
        raise RuntimeError(f'Pointer moved outside the intended trace during {phase}: {position}, expected {expected}.')
    fixed = str(heading.rectangle()) == initial
    if not fixed:
        raise RuntimeError('Pull moved the content.')
    left, top = win32gui.ClientToScreen(window.handle, (0, 0))
    rect = win32gui.GetClientRect(window.handle)
    ImageGrab.grab(bbox=(left, top, left+rect[2], top+rect[3]), all_screens=True).save(output/f'{phase}.png')
    records.append({'phase':phase, 'mouse_down':down, 'heading_fixed':fixed, 'pointer':win32gui.GetCursorPos(), 'seconds':round(time.perf_counter()-started,3)})

def move(dx, dy):
    width = ctypes.windll.user32.GetSystemMetrics(0)
    height = ctypes.windll.user32.GetSystemMetrics(1)
    # A real move event is necessary: SetCursorPos alone can move the cursor while
    # WinUI's captured PointerPoint still contains its old coordinates.
    ctypes.windll.user32.mouse_event(0x8001, round((start[0]+dx)*65535/(width-1)), round((start[1]+dy)*65535/(height-1)), 0, 0)
    time.sleep(.55)

ctypes.windll.user32.SetCursorPos(*start)
time.sleep(.5)
capture('rest', expected=start)
try:
    ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)
    move(0, -110)
    capture('pull', held=True, expected=(start[0],start[1]-110))
    move(0, 90)
    capture('reverse', held=True, expected=(start[0],start[1]+90))
finally:
    ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)
for index in range(8):
    time.sleep(.055)
    capture(f'recoil-{index+1:02}')
ctypes.windll.user32.SetCursorPos(h.left-70, h.top-100)
time.sleep(1.2)
capture('settled', expected=(h.left-70,h.top-100))
button = window.child_window(auto_id='AnchoredButton')
before = int(button.window_text().rsplit(' ', 1)[-1])
rect = button.rectangle()
ctypes.windll.user32.SetCursorPos((rect.left+rect.right)//2, (rect.top+rect.bottom)//2)
ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)
ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)
time.sleep(.15)
if int(button.window_text().rsplit(' ', 1)[-1]) != before + 1:
    raise RuntimeError('Native mouse click did not reach the button exactly once.')
entry = window.child_window(auto_id='AnchoredEntry')
entry.set_edit_text('native input remains editable')
if entry.get_value() != 'native input remains editable':
    raise RuntimeError('Native input was intercepted.')
entry.set_edit_text('')
rest = Image.open(output/'rest.png').convert('RGB')
pull = Image.open(output/'pull.png').convert('RGB')
outside = (edge_x-55,edge_y-28,edge_x+55,edge_y-2)
change = sum(ImageStat.Stat(ImageChops.difference(rest,pull).crop(outside)).mean)/3
if change < 1:
    raise RuntimeError('The visible edge did not bulge outside the layout: check clipping and actual pointer delivery.')
(output/'pointer.json').write_text(json.dumps({'states':records, 'native_click':True, 'native_edit':True, 'outside_edge_change':change, 'dpi':ctypes.windll.user32.GetDpiForWindow(window.handle)},indent=2),encoding='utf-8')
print(json.dumps(records))
