"""Compare observable stable/changing image regions. Requires Pillow; no image editing.

Rectangles are x,y,width,height in pixels. Use --channels alpha for silhouette tests.
"""
import argparse
import json
from PIL import Image, ImageChops, ImageStat

def region(value):
    try:
        x,y,w,h = map(int,value.split(','))
        if min(x,y) < 0 or min(w,h) <= 0: raise ValueError()
        return x,y,x+w,y+h
    except ValueError:
        raise argparse.ArgumentTypeError('Expected nonnegative x,y and positive width,height')

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('rest')
parser.add_argument('deformed')
parser.add_argument('--stable-region',type=region,action='append',default=[])
parser.add_argument('--changed-region',type=region,action='append',default=[])
parser.add_argument('--channels',choices=['rgba','rgb','alpha'],default='rgba')
parser.add_argument('--stable-max',type=float,default=1)
parser.add_argument('--min-change',type=float,default=3)
args=parser.parse_args()
if not args.stable_region or not args.changed_region: parser.error('Specify both stable and changed regions')
a=Image.open(args.rest).convert('RGBA')
b=Image.open(args.deformed).convert('RGBA')
if a.size != b.size: parser.error('Capture dimensions differ; compare the same viewport and DPI')
if args.channels=='alpha': a,b=a.getchannel('A'),b.getchannel('A')
elif args.channels=='rgb': a,b=a.convert('RGB'),b.convert('RGB')
diff=ImageChops.difference(a,b)
checks=[]
for kind,regions in [('stable',args.stable_region),('changed',args.changed_region)]:
    for box in regions:
        if box[2]>a.width or box[3]>a.height: parser.error('Region exceeds capture bounds')
        stat=ImageStat.Stat(diff.crop(box))
        mean=sum(stat.mean)/len(stat.mean)
        peak=max(high for low,high in stat.extrema)
        passed=peak<=args.stable_max if kind=='stable' else mean>=args.min_change
        checks.append(dict(kind=kind,box=box,mean=mean,peak=peak,passed=passed))
print(json.dumps(checks,indent=2))
raise SystemExit(0 if all(check['passed'] for check in checks) else 1)
