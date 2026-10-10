"""Bind the unchanged reference PNG to a Spine weighted mesh.

No image painting, cropping, resampling or re-generation occurs here. Only
Spine geometry, inverse-bind coordinates, skin weights and timelines change.
"""
from pathlib import Path
import hashlib
import json
import math
import shutil
import struct

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'idle-v2'
SOURCE = ROOT.parent / 'megumin-concepts-20261009/quartet/idle-02-right-hand.png'
for folder in [OUT / 'export', OUT / 'images']:
    folder.mkdir(parents=True, exist_ok=True)
png = SOURCE.read_bytes()
W, H = struct.unpack('>II', png[16:24])
S = 320 / 1320
OX, OY = 608, 1348

def world(x, y):
    return ((x - OX) * S, (OY - y) * S)

bones, origins, bone_ids = [], {}, {}

def bone(name, x, y, parent='root', length=0):
    wx, wy = world(x, y)
    px, py = origins.get(parent, (0, 0))
    data = dict(name=name, x=round(wx-px, 8), y=round(wy-py, 8))
    if name != 'root':
        data['parent'] = parent
    if length:
        data['length'] = length
    bone_ids[name] = len(bones)
    bones.append(data)
    origins[name] = wx, wy

bone('root', OX, OY)
bone('torso', 620, 970, length=24)
bone('chest', 623, 743, 'torso', 20)
bone('head', 636, 655, 'chest', 24)
bone('hat', 605, 367, 'head', 25)
bone('hair_left', 495, 643, 'head', 14)
bone('hair_right', 744, 640, 'head', 14)
bone('arm_free', 714, 780, 'chest', 25)
bone('cape_left', 440, 935, length=24)
bone('cape_right', 756, 1008, length=20)
bone('staff', 310, 887, length=35)
bone('grip_right', 310, 887, 'staff', 8)
bone('foot_right', 519, 1332, length=15)
bone('foot_left', 686, 1329, length=15)

def smooth(a, b, x):
    t = min(1., max(0., (x-a)/(b-a)))
    return t*t*(3-2*t)

def inside(x, y, polygon):
    hit = False
    for (ax, ay), (bx, by) in zip(polygon, polygon[1:]+polygon[:1]):
        if (ay > y) != (by > y) and x < (bx-ax)*(y-ay)/(by-ay)+ax:
            hit = not hit
    return hit

def segment_distance(x, y, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    t = min(1., max(0., ((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)))
    return math.hypot(x-a[0]-t*dx, y-a[1]-t*dy)

# These regions affect only the deformation weights, never the source pixels.
staff_top = [(27,169),(130,169),(153,345),(217,376),(279,464),
             (286,570),(255,624),(294,739),(248,762),(194,667),
             (128,604),(112,470),(93,429),(26,272)]
cape_left = [(440,834),(523,800),(556,892),(515,1000),(491,1115),
             (461,1163),(349,1206),(329,1181),(368,1020)]
cape_right = [(714,1007),(763,984),(808,1070),(816,1205),(710,1160),
              (697,1120)]

def weights(x, y):
    # Protect the complete prop silhouette and the grasp, with a margin wider
    # than one grid cell so triangles crossing the visible boundary stay rigid.
    shaft_dist = segment_distance(x, y, (247,700), (411,1308))
    if inside(x,y,staff_top) or shaft_dist < 52 or (y>1190 and x<483):
        return {'staff': 1.}
    if 256 <= x <= 358 and 814 <= y <= 952:
        return {'grip_right': 1.}
    if y >= 1200:
        return {'foot_right' if x < 598 else 'foot_left': 1.}
    if inside(x,y,cape_left):
        return {'cape_left': 1.}
    if inside(x,y,cape_right):
        return {'cape_right': 1.}
    if y < 425:
        return {'hat': 1.}
    if y < 635:
        h = smooth(420,510,y)
        return {'head':h, 'hat':1-h}
    if 406 < x < 563 and y < 801:
        h = smooth(632,760,y)
        return {'head':1-h*.55, 'hair_left':h*.55}
    if 700 < x < 791 and y < 806:
        h = smooth(640,768,y)
        return {'head':1-h*.55, 'hair_right':h*.55}
    if y < 752:
        h = smooth(650,748,y)
        return {'head':1-h,'chest':h}
    if x > 706 and y < 1100:
        return {'arm_free':1.}
    if y < 975:
        h = smooth(770,950,y)
        # Shoulder follows breathing; the sleeve eases to the fixed grasp.
        lock = 1-smooth(341,471,x) if x<500 else 0
        return {'chest':(1-h)*(1-lock),'torso':h*(1-lock),'grip_right':lock}
    return {'torso':1-smooth(975,1040,y),'root':smooth(975,1040,y)}

# Hull first, clockwise in texture coordinates; Spine imports this as an
# editable grid mesh. Shared vertices prevent cracks between neighboring parts.
xs, ys = list(range(0,W,24))+[W], list(range(0,H,24))+[H]
boundary = ([(x,0) for x in xs] + [(W,y) for y in ys[1:]] +
            [(x,H) for x in reversed(xs[:-1])] + [(0,y) for y in reversed(ys[1:-1])])
points = boundary + [(x,y) for y in ys[1:-1] for x in xs[1:-1]]
ids = {p:i for i,p in enumerate(points)}
triangles = []
for ya,yb in zip(ys,ys[1:]):
    for xa,xb in zip(xs,xs[1:]):
        a,b,c,d = [ids[p] for p in [(xa,ya),(xb,ya),(xb,yb),(xa,yb)]]
        triangles.extend([a,d,b,b,d,c])

vertices, uvs, expected, locked, influences = [], [], [], [], {}
for index,(x,y) in enumerate(points):
    wx,wy = world(x,y)
    uvs.extend([x/W,y/H])
    expected.extend([wx,wy])
    weight = {k:v for k,v in weights(x,y).items() if v>1e-8}
    total = sum(weight.values())
    vertices.append(len(weight))
    for name,w in weight.items():
        bx,by = origins[name]
        vertices.extend([bone_ids[name],round(wx-bx,8),round(wy-by,8),w/total])
        influences[name] = influences.get(name,0)+1
    if set(weight) <= {'root','staff','grip_right','foot_left','foot_right'}:
        locked.append(index)

tracks = {}
def track(name, channel, fn):
    tracks.setdefault(name,{})[channel] = [dict(time=round(i/30,7),**fn(i/30)) for i in range(121)]
def wave(t):return math.sin(t/4*math.tau)
track('torso','translate',lambda t:dict(x=0,y=round(.25*wave(t),7)))
track('chest','translate',lambda t:dict(x=round(.055*wave(t),7),y=round(.31*wave(t),7)))
track('head','rotate',lambda t:dict(value=round(.025*wave(t),7)))
track('hat','rotate',lambda t:dict(value=round(-.035*wave(t),7)))
track('hair_left','rotate',lambda t:dict(value=round(.10*wave(t),7)))
track('hair_right','rotate',lambda t:dict(value=round(-.08*wave(t),7)))
track('arm_free','translate',lambda t:dict(x=0,y=round(.035*wave(t),7)))
track('cape_left','translate',lambda t:dict(x=round(-.22*wave(t),7),y=round(.10*wave(t),7)))
track('cape_right','translate',lambda t:dict(x=round(.18*wave(t),7),y=round(.08*wave(t),7)))

mesh = dict(type='mesh',path='idle-reference',uvs=uvs,triangles=triangles,
            vertices=vertices,hull=len(boundary),width=W*S,height=H*S)
raw = dict(skeleton=dict(hash='megumin-idle-v2-reference-preserved',spine='4.2.11',
                         x=-OX*S,y=(OY-H)*S,width=W*S,height=H*S,images='../images/',fps=30),
           bones=bones,slots=[dict(name='reference_mesh',bone='root',attachment='idle-reference')],
           skins=[dict(name='default',attachments={'reference_mesh':{'idle-reference':mesh}})],
           animations={'idle_loop':{'bones':tracks},'setup_pose':{'bones':{'root':{'translate':[{'time':0,'x':0,'y':0},{'time':4,'x':0,'y':0}]}}}})
text = json.dumps(raw,ensure_ascii=False,separators=(',',':'))
for filename in ['megumin-idle.json','megumin-idle.spine-json']:
    (OUT/'export'/filename).write_text(text,encoding='utf-8')
for target in [OUT/'export/idle-reference.png',OUT/'images/idle-reference.png']:
    shutil.copyfile(SOURCE,target)
(OUT/'export/megumin-idle.atlas').write_text(f'''idle-reference.png
size: {W},{H}
format: RGBA8888
filter: Linear,Linear
repeat: none
pma: false
idle-reference
  rotate: false
  xy: 0, 0
  size: {W}, {H}
  orig: {W}, {H}
  offset: 0, 0
  index: -1
''',encoding='utf-8')
manifest = dict(source=str(SOURCE.relative_to(ROOT.parent)),texture_sha256=hashlib.sha256(png).hexdigest(),
                texture_unchanged=True,source_size=[W,H],source_origin=[OX,OY],scale=S,
                bones=len(bones),vertices=len(points),triangles=len(triangles)//3,
                weighted_bones=influences,loop_seconds=4,scope='Corrected idle only; v1 action prototype retained separately.',
                limitations=['Single continuous weighted mesh supports subtle idle only.',
                             'Large poses need faithful layers and hidden-area artwork.',
                             'No blink or replacement face; no Spine editor or game import verified.'])
(OUT/'export/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'bind-check.json').write_text(json.dumps(dict(expected_world=expected,fixed_vertex_indices=locked),separators=(',',':')),encoding='utf-8')
print(json.dumps({k:manifest[k] for k in ['texture_unchanged','bones','vertices','triangles','loop_seconds']},indent=2))
