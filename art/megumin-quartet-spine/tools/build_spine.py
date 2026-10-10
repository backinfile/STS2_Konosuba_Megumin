"""Reproducible Spine 4.2 rig and atlas builder.

Artwork is generated separately. Pillow only performs lossless rectangular
atlas extraction; this script does not paint or retouch the artwork.
"""
from pathlib import Path
from PIL import Image
import json
import math
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "export"
IMAGES = ROOT / "images"
OUT.mkdir(exist_ok=True)
IMAGES.mkdir(exist_ok=True)

# Source sheet coordinates, measured against the generated PNGs.
SHEETS = {
    "standing-parts.png": {
        "head": (0, 20, 365, 412), "hat": (365, 30, 790, 410),
        "dress": (790, 20, 1040, 400), "cape": (1050, 0, 1448, 400),
        "upper_r": (60, 413, 300, 699), "upper_l": (445, 412, 680, 699),
        "fore_r": (745, 465, 1040, 640), "fore_l_open": (1150, 407, 1390, 698),
        "leg_r": (90, 699, 265, 1070), "leg_l": (470, 699, 665, 1070),
        "staff": (840, 646, 974, 1086), "fore_l_grip": (1120, 770, 1430, 975),
    },
    "expressions-down.png": {
        "head_blink": (15, 20, 478, 452), "head_chant": (526, 20, 982, 452),
        "head_hurt": (1070, 20, 1524, 452), "sit": (18, 456, 486, 1000),
        "supine": (454, 495, 1039, 1012), "defeat": (1042, 550, 1535, 1009),
    },
    "upper-connectors.png": {
        "upper_r_clean": (400, 130, 745, 765),
        "upper_l_clean": (1030, 130, 1380, 765),
    },
}
regions = {}
atlas = []
for filename, pieces in SHEETS.items():
    im = Image.open(ROOT / "source" / filename).convert("RGBA")
    shutil.copyfile(ROOT / "source" / filename, OUT / filename)
    atlas.extend([filename, f"size: {im.width},{im.height}", "format: RGBA8888", "filter: Linear,Linear", "repeat: none", "pma: false"])
    for name, box in pieces.items():
        crop = im.crop(box)
        # Ignore nearly transparent generation residue when choosing a region.
        # The extracted pixels and their original alpha are otherwise unchanged.
        bounds = crop.getchannel("A").point(lambda a: 255 if a > 32 else 0).getbbox()
        if not bounds:
            raise ValueError(f"Empty region: {name}")
        x = box[0] + max(0, bounds[0] - 2)
        y = box[1] + max(0, bounds[1] - 2)
        right = min(box[2], box[0] + bounds[2] + 2)
        bottom = min(box[3], box[1] + bounds[3] + 2)
        w, h = right-x, bottom-y
        regions[name] = {"page": filename, "x": x, "y": y, "w": w, "h": h}
        im.crop((x, y, right, bottom)).save(IMAGES / f"{name}.png")
        atlas.extend([name, "  rotate: false", f"  xy: {x}, {y}", f"  size: {w}, {h}", f"  orig: {w}, {h}", "  offset: 0, 0", "  index: -1"])
    atlas.append("")
(OUT / "megumin.atlas").write_text("\n".join(atlas), encoding="utf-8")
(ROOT / "source" / "regions.json").write_text(json.dumps(regions, indent=2), encoding="utf-8")

bones = []
def bone(name, parent=None, x=0, y=0, **kw):
    item = dict(name=name, x=x, y=y, **kw)
    if parent:
        item["parent"] = parent
    bones.append(item)

bone("root")
bone("body", "root", 0, 85)
bone("chest", "body", 0, 90)
bone("cape", "chest", 0, -2)
bone("head", "chest", 0, 15)
bone("hat", "head", -18, 141)
bone("leg_r", "root", -21, 0)
bone("leg_l", "root", 22, 0)
bone("staff", "root", -94, 138)
bone("grip_r", "staff")
bone("grip_l", "root", 40, 105)
bone("arm_r", "chest", -30, 0, length=35)
bone("fore_r", "arm_r", 35, 0, length=43)
bone("arm_l", "chest", 30, 0, length=32)
bone("fore_l", "arm_l", 32, 0, length=36)
bone("down_pose", "root")

slots, attachments = [], {}
def region(slot, bone_name, image, x=0, y=0, width=None, height=None, rotation=0, default=True):
    r = regions[image]
    if width is None:
        width = height * r["w"] / r["h"]
    if height is None:
        height = width * r["h"] / r["w"]
    a = dict(type="region", path=image, x=round(x, 4), y=round(y, 4), width=round(width, 4), height=round(height, 4), rotation=round(rotation, 4))
    if slot not in attachments:
        slots.append(dict(name=slot, bone=bone_name, attachment=image if default else None))
        attachments[slot] = {}
    attachments[slot][image] = a
    return a

def anchored(slot, bone_name, name, pivot, endpoint, length, default=True):
    """Orient the source limb's joint-to-hand axis along its Spine bone's +X."""
    r = regions[name]
    dx, dy = endpoint[0]-pivot[0], pivot[1]-endpoint[1]
    angle = -math.atan2(dy, dx)
    scale = length / math.hypot(dx, dy)
    cx = (r["x"] + r["w"]/2 - pivot[0]) * scale
    cy = (pivot[1] - r["y"] - r["h"]/2) * scale
    x, y = cx*math.cos(angle)-cy*math.sin(angle), cx*math.sin(angle)+cy*math.cos(angle)
    return region(slot, bone_name, name, x, y, width=r["w"]*scale, rotation=math.degrees(angle), default=default)

region("cape", "cape", "cape", 0, -65, height=148)
region("leg_l", "leg_l", "leg_l", 0, 48, height=98)
region("leg_r", "leg_r", "leg_r", 0, 48, height=98)
anchored("upper_l", "arm_l", "upper_l_clean", (1180, 211), (1264, 682), 32)
anchored("upper_r", "arm_r", "upper_r_clean", (590, 211), (509, 682), 35)
region("dress", "body", "dress", 0, 53, height=123)
# Staff pivot is the anatomical right hand's immutable primary grip.
r = regions["staff"]
s = 325/r["h"]
region("staff", "staff", "staff", (r["x"]+r["w"]/2-927)*s, (897-r["y"]-r["h"]/2)*s, height=325)
anchored("fore_r", "fore_r", "fore_r", (1000, 516), (790, 549), 43)
anchored("fore_l", "fore_l", "fore_l_open", (1295, 436), (1250, 637), 36)
anchored("fore_l", "fore_l", "fore_l_grip", (1190, 820), (1374, 900), 36)
region("head", "head", "head", 0, 44, width=185)
for name in ["head_blink", "head_chant", "head_hurt"]:
    region("head", "head", name, 0, 44, width=185)
region("hat", "hat", "hat", 0, 0, width=230)
for name, scale, x in [("sit", .50, 0), ("supine", .50, 15), ("defeat", .56, 8)]:
    r = regions[name]
    region("down", "down_pose", name, x, r["h"]*scale/2, width=r["w"]*scale, default=False)

def mesh_outline(name, polygon):
    """Use a Spine mesh outline to exclude neighboring sheet pieces.

    This only specifies runtime UV geometry: the atlas pixels are unchanged.
    The two narrow indentations follow the transparent gap between drawings.
    """
    a=attachments["down"][name]; r=regions[name]
    points=[(max(0,min(1,(x-r["x"])/r["w"])),max(0,min(1,(y-r["y"])/r["h"]))) for x,y in polygon]
    # Ear clipping of a simple polygon in source image (clockwise visually).
    def cross(a,b,c): return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    def inside(p,a,b,c): return cross(a,b,p)>=0 and cross(b,c,p)>=0 and cross(c,a,p)>=0
    indices=list(range(len(points))); triangles=[]
    while len(indices)>3:
        for j,b in enumerate(indices):
            aidx,c=indices[j-1],indices[(j+1)%len(indices)]
            if cross(points[aidx],points[b],points[c])<=0: continue
            if any(inside(points[k],points[aidx],points[b],points[c]) for k in indices if k not in [aidx,b,c]): continue
            triangles.extend([aidx,b,c]); indices.pop(j); break
        else: raise ValueError("Cannot triangulate "+name)
    triangles.extend(indices)
    vertices=[]
    for u,v in points: vertices.extend([round(a["x"]+(u-.5)*a["width"],5),round(a["y"]+(.5-v)*a["height"],5)])
    attachments["down"][name]=dict(type="mesh",path=name,uvs=[round(v,7) for p in points for v in p],triangles=triangles,vertices=vertices,hull=len(points),width=a["width"],height=a["height"])

mesh_outline("sit",[(18,456),(486,456),(486,620),(445,620),(445,735),(486,735),(486,1000),(18,1000)])
mesh_outline("supine",[(494,495),(1039,495),(1039,1012),(494,1012),(494,727),(454,727),(454,625),(494,625)])

# Upper cuffs cover the rounded elbow overlap from each forearm drawing.
order=["cape","leg_l","leg_r","dress","staff","fore_r","fore_l","upper_r","upper_l","head","hat","down"]
slots.sort(key=lambda s:order.index(s["name"]))
standing_slots = [s["name"] for s in slots if s["name"] != "down"]
default_at = {s["name"]: s["attachment"] for s in slots}

def mix(a, b, t):
    return a+(b-a)*t
def smooth(t):
    return t*t*(3-2*t)
IDLE = dict(body_y=0, body_r=0, head_r=0, cape_r=0, hat_r=0, staff_x=-94, staff_y=138, staff_r=8, left_x=40, left_y=105, leg_r=0, leg_l=0)
CHANT = dict(IDLE, body_r=-2, head_r=1, staff_x=18, staff_y=144, staff_r=-72)
RELEASE = dict(CHANT, body_r=-7, head_r=3, staff_x=30, staff_y=151, staff_r=-80, cape_r=7, hat_r=2)
TIRED = dict(IDLE, body_y=-17, body_r=4, head_r=-12, staff_x=-80, staff_y=114, staff_r=-12, left_x=42, left_y=92, leg_r=5, leg_l=-4)

def blend(a,b,t):
    return {k:mix(a[k],b[k],t) for k in IDLE}
def two_hand(p):
    p = dict(p)
    a = math.radians(p["staff_r"])
    p["left_x"] = p["staff_x"] - 55*math.sin(a)
    p["left_y"] = p["staff_y"] + 55*math.cos(a)
    return p
CHANT, RELEASE = two_hand(CHANT), two_hand(RELEASE)

animations = {}
def sampled(name, duration, pose, head="head", grip=False, events=None):
    tracks = {b:{} for b in ["body", "head", "cape", "hat", "staff", "grip_l", "leg_r", "leg_l"]}
    for i in range(round(duration*60)+1):
        t = min(duration, i/60)
        p = pose(t)
        def add(b, channel, **v):
            tracks[b].setdefault(channel, []).append(dict(time=round(t,5), **{k:round(x,5) for k,x in v.items()}))
        add("body", "translate", x=0, y=p["body_y"])
        add("body", "rotate", value=p["body_r"])
        for b in ["head", "cape", "hat", "leg_r", "leg_l"]:
            add(b,"rotate",value=p[b+"_r"] if b in ["head", "cape", "hat"] else p[b])
        add("staff","translate",x=p["staff_x"]-IDLE["staff_x"], y=p["staff_y"]-IDLE["staff_y"])
        add("staff","rotate",value=p["staff_r"])
        add("grip_l","translate",x=p["left_x"]-40, y=p["left_y"]-105)
    anim = dict(bones=tracks, slots={"head":{"attachment":[dict(time=0,name=head)]}, "fore_l":{"attachment":[dict(time=0,name="fore_l_grip" if grip else "fore_l_open")]}})
    if events:
        anim["events"] = events
    animations[name] = anim
    return anim

def through(keys, t):
    for (a,pa),(b,pb) in zip(keys,keys[1:]):
        if t <= b:
            return blend(pa,pb,smooth(max(0,(t-a)/(b-a))))
    return dict(keys[-1][1])

def idle(t):
    k = math.sin(t/3*math.tau)
    return dict(IDLE, body_y=.95*k, head_r=.45*k, cape_r=1.1*math.sin(t/3*math.tau-.3),hat_r=-.2*k)
a = sampled("idle_loop",3,idle)
a["slots"]["head"]["attachment"] = [dict(time=0,name="head"),dict(time=2.15,name="head_blink"),dict(time=2.27,name="head"),dict(time=3,name="head")]

cast = dict(IDLE,left_x=62,left_y=179,head_r=3,cape_r=-2)
a = sampled("cast_short",.65,lambda t:through([(0,IDLE),(.18,cast),(.36,cast),(.65,IDLE)],t))
a["slots"]["head"]["attachment"]=[dict(time=0,name="head"),dict(time=.16,name="head_blink"),dict(time=.40,name="head")]
sampled("chant_enter",.6,lambda t:blend(IDLE,CHANT,smooth(t/.6)),"head_chant",True)
def chanting(t):
    k=math.sin(t/2*math.tau)
    return two_hand(dict(CHANT,body_y=.65*k,head_r=1+.35*k,cape_r=1.2*k,hat_r=-.25*k))
sampled("chant_loop",2,chanting,"head_chant",True)
sampled("chant_cancel",.45,lambda t:blend(CHANT,IDLE,smooth(t/.45)),"head",True)["slots"]["fore_l"]["attachment"].append(dict(time=.34,name="fore_l_open"))
sampled("chant_ack",.5,lambda t:dict(CHANT,head_r=1-4*math.sin(t/.5*math.pi)),"head_chant",True)
short = dict(IDLE,body_r=-4,staff_x=-49,staff_y=153,staff_r=-42,head_r=2,cape_r=4,left_x=45,left_y=120)
sampled("attack_short",.65,lambda t:through([(0,IDLE),(.15,dict(IDLE,body_r=2)),(.27,short),(.39,short),(.65,IDLE)],t),events=[dict(time=.27,name="impact",string="ordinary")])
wind=two_hand(dict(CHANT,body_r=3,staff_x=10,staff_y=148,staff_r=-63,head_r=-2))
sampled("explosion_release",.6,lambda t:through([(0,CHANT),(.28,wind),(.40,RELEASE),(.6,RELEASE)],t),"head_chant",True,[dict(time=.40,name="release",string="explosion")])
sampled("explosion_hold",.6,lambda t:two_hand(dict(RELEASE,cape_r=7+math.sin(t/.6*math.tau)*.45)),"head_chant",True)
sampled("explosion_exit",.35,lambda t:blend(RELEASE,TIRED,smooth(t/.35)),"head_hurt",True)

for name,base,grip in [("hit",IDLE,False),("hit_chant",CHANT,True)]:
    recoil=dict(base,body_r=base["body_r"]+6,body_y=-3,head_r=-7,cape_r=-5,hat_r=-3)
    sampled(name,.4,lambda t,b=base,r=recoil:through([(0,b),(.08,r),(.16,r),(.4,b)],t),"head_hurt",grip)["slots"]["head"]["attachment"].append(dict(time=.3,name="head_chant" if grip else "head"))

def down_visibility(anim, transitions):
    # Discrete attachment swaps use dedicated perspective drawings for the fall.
    for slot in standing_slots:
        anim.setdefault("slots",{})[slot] = {"attachment":[dict(time=t,name=default_at[slot] if pose is None else None) for t,pose in transitions]}
    anim["slots"]["down"]={"attachment":[dict(time=t,name=pose) for t,pose in transitions]}

a=sampled("relaxed_fall",.8,lambda t:through([(0,TIRED),(.30,dict(TIRED,body_y=-33,head_r=-17)),(.8,TIRED)],t),"head_hurt")
down_visibility(a,[(0,None),(.30,"sit"),(.56,"supine")])
a["bones"]["down_pose"]={"translate":[dict(time=.3,x=0,y=5),dict(time=.4,x=0,y=0),dict(time=.56,x=0,y=4),dict(time=.72,x=0,y=0),dict(time=.8,x=0,y=0)]}
a={"bones":{"down_pose":{"scale":[dict(time=0,x=1,y=1),dict(time=1,x=1,y=1.006),dict(time=2,x=1,y=1)]}}}
down_visibility(a,[(0,"supine")]); animations["relaxed_loop"]=a
a=sampled("get_up",.95,lambda t:through([(0,TIRED),(.55,dict(TIRED,body_y=-28)),(.95,IDLE)],t))
down_visibility(a,[(0,"supine"),(.20,"sit"),(.55,None)])
a["bones"]["down_pose"]={"translate":[dict(time=0,x=0,y=0),dict(time=.20,x=0,y=0),dict(time=.5,x=0,y=8)]}
a=sampled("dead",.9,lambda t:through([(0,IDLE),(.16,dict(IDLE,body_y=-8,head_r=-9)),(.45,dict(TIRED,body_r=24,body_y=-34)),(.9,TIRED)],t),"head_hurt")
down_visibility(a,[(0,None),(.45,"defeat")])
a["bones"]["down_pose"]={"translate":[dict(time=.45,x=0,y=4),dict(time=.65,x=0,y=0),dict(time=.9,x=0,y=0)]}
a={"bones":{"down_pose":{"translate":[dict(time=0,x=0,y=0),dict(time=.35,x=0,y=0)]}}}; down_visibility(a,[(0,"supine"),(.2,"defeat")]); animations["dead_from_down"]=a
a={"bones":{"down_pose":{"translate":[dict(time=0,x=0,y=0),dict(time=.06,x=-3,y=0),dict(time=.28,x=0,y=0)]}}}; down_visibility(a,[(0,"supine")]); animations["hit_down"]=a

data={
 "skeleton":{"hash":"megumin-quartet-v1", "spine":"4.2.11", "x":-190,"y":-10,"width":450,"height":440,"images":"../images/","fps":60},
 "bones":bones,
 "slots":slots,
 "ik":[dict(name="right_hand_lock",order=0,bones=["arm_r","fore_r"],target="grip_r",mix=1,bendPositive=False),dict(name="left_hand_lock",order=1,bones=["arm_l","fore_l"],target="grip_l",mix=1,bendPositive=True)],
 "skins":[{"name":"default","attachments":attachments}],
 "events":{"impact":{"string":"ordinary"},"release":{"string":"explosion"}},
 "animations":animations,
}
content=json.dumps(data,ensure_ascii=False,separators=(",",":"))
(OUT/"megumin.json").write_text(content,encoding="utf-8")
(OUT/"megumin.spine-json").write_text(content,encoding="utf-8")
manifest={"version":"0.1.0", "spine":"4.2.11", "artwork":"Built-in imagegen; original PNGs preserved in source/", "reference_model":"../megumin-concepts-20261009/quartet/idle-02-right-hand.png", "bones":len(bones), "slots":len(slots), "attachments":sum(len(a) for a in attachments.values()), "atlas_regions":len(regions), "animations":list(animations), "limitations":["Standing rig uses rigid region attachments and two arm IK constraints.","Sitting/supine/defeat use whole-pose attachment replacements; fall/get-up transitions are prototype blocking. Two outlined meshes exclude adjacent sheet fragments without altering source pixels.","Not integrated into the playable STS2 mod; no native .spine or binary .skel was authored."]}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
# Vendored official browser runtime with its original license for offline preview.
vendor=ROOT/"vendor"; vendor.mkdir(exist_ok=True)
pkg=ROOT/"node_modules/@esotericsoftware/spine-webgl"
if pkg.exists():
    shutil.copyfile(pkg/"dist/iife/spine-webgl.min.js",vendor/"spine-webgl-4.2.95.min.js")
    shutil.copyfile(pkg/"LICENSE",vendor/"SPINE-RUNTIME-LICENSE.txt")
print(json.dumps(manifest,ensure_ascii=False,indent=2))
