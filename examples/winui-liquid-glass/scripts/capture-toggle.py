"""Real pointer/keyboard/UIA tests for the glass switch. No product settings are used."""
import ctypes,json,sys,time,win32gui,win32process
from pathlib import Path
from pywinauto import Application
from PIL import ImageGrab,ImageChops,ImageStat
pid=int(sys.argv[1]);handles=[]
win32gui.EnumWindows(lambda h,_: handles.append(h) if win32gui.IsWindowVisible(h)
                    and win32process.GetWindowThreadProcessId(h)[1]==pid else None,None)
if len(handles)!=1:raise RuntimeError(f'Expected one demo window: {handles}')
win32gui.ShowWindow(handles[0],9)
w=Application(backend='uia').connect(process=pid).window(handle=handles[0]);w.set_focus();time.sleep(.15)
t=w.child_window(auto_id='GlassToggle').wrapper_object()
output=Path(sys.argv[2]);output.mkdir(parents=True,exist_ok=True)
u=ctypes.windll.user32
r=t.rectangle();dpi=u.GetDpiForWindow(w.handle)/96
left=int(r.left+13*dpi);right=int(left+22*dpi);cy=(r.top+r.bottom)//2
rows=[]
last_pointer=None
def move(x,y,delay=.16):
 global last_pointer
 u.mouse_event(0x8001,round(x*65535/(u.GetSystemMetrics(0)-1)),round(y*65535/(u.GetSystemMetrics(1)-1)),0,0);time.sleep(delay)
 if max(abs(a-b) for a,b in zip(win32gui.GetCursorPos(),(x,y)))>6: raise RuntimeError('Input interrupted')
 last_pointer=(x,y)
def down():u.mouse_event(2,0,0,0,0)
def up():u.mouse_event(4,0,0,0,0)
def state():return t.iface_toggle.CurrentToggleState
def capture(phase,expected,held=False):
 if win32gui.GetForegroundWindow()!=w.handle:raise RuntimeError('Not foreground')
 if bool(u.GetAsyncKeyState(1)&0x8000)!=held:raise RuntimeError('Unexpected pointer held state')
 if held and last_pointer is not None and max(abs(a-b) for a,b in zip(win32gui.GetCursorPos(),last_pointer))>6:raise RuntimeError('Held pointer input interrupted')
 actual=state()
 if actual!=expected:raise RuntimeError(f'{phase}: {actual} vs {expected}')
 x,y=win32gui.ClientToScreen(w.handle,(0,0));cr=win32gui.GetClientRect(w.handle)
 shot=ImageGrab.grab(bbox=(x,y,x+cr[2],y+cr[3]),all_screens=True)
 shot.save(output/(phase+'.png'))
 rows.append({'phase':phase,'state':actual,'held':held})
 return shot
if state():t.iface_toggle.Toggle()
time.sleep(.5)
capture('off',0)
try:
 move(left,cy);down();time.sleep(.2);capture('pressed',0,True)
 move(right,cy,.3);capture('preview-right',0,True)
 move(left,cy,.3);capture('preview-left',0,True)
 move(right,cy,.15)
finally:up()
time.sleep(.6);capture('on',1)
try:
 move(right,cy);down();time.sleep(.4);capture('on-pressed',1,True)
 move(left,cy,.3);capture('preview-off',1,True)
finally:up()
time.sleep(.6);capture('off-again',0)
try:
 move(left,cy);down();move(right,cy,.2);t.type_keys('{ESC}')
finally:up()
time.sleep(.5);capture('cancelled',0)
t.set_focus();t.type_keys('{SPACE}');time.sleep(.5);capture('keyboard-on',1)
t.iface_toggle.Toggle();time.sleep(.5);capture('automation-off',0)
if '--compare-optics' in sys.argv:
 compare=w.child_window(auto_id='BlurOnly')
 if compare.get_toggle_state():compare.toggle()
 def held_frame(phase):
  if not state():t.iface_toggle.Toggle()
  time.sleep(.6)
  try:
   move(right,cy);down();time.sleep(.65)
   return capture(phase,1,True)
  finally:up()
 glass=held_frame('on-held-glass')
 time.sleep(.6)
 compare.toggle();time.sleep(.4)
 flat=held_frame('on-held-flat')
 time.sleep(.6);compare.toggle()
 x,y=win32gui.ClientToScreen(w.handle,(0,0))
 cx=right+3*dpi-x;center_y=cy-y
 box=(round(cx-27*dpi),round(center_y-17*dpi),round(cx+27*dpi),round(center_y+17*dpi))
 glass.crop(box).save(output/'switch-glass-crop.png');flat.crop(box).save(output/'switch-flat-crop.png')
 difference=sum(ImageStat.Stat(ImageChops.difference(glass.crop(box),flat.crop(box))).mean[:3])/3
 if difference<2:raise RuntimeError(f'Native switch has no visible refraction: {difference}')
 rows.append({'comparison':'same stationary held pose','mean_pixel_difference':difference,'dpi':dpi})
(output/'toggle.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps(rows))
