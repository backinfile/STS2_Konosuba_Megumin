"""Independent five-state review using the existing offline triangle rasterizer.

Does not edit source images, rig, mesh, or any animation resource. The output is
clearly labeled as software rasterization of exported Godot geometry.
"""
from pathlib import Path
import os
import sys
import time
import importlib.util
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'preview/five_states'
os.environ['MEGUMIN_RENDER_DIR'] = str(OUT)
spec = importlib.util.spec_from_file_location('v6_existing_raster', ROOT/'tools/render_software_review.py')
raster = importlib.util.module_from_spec(spec)
spec.loader.exec_module(raster)
DATA = raster.DATA
FONT = raster.FONT
W, H = raster.W, raster.H


def phase(state, t):
    if state == 'Idle':
        return 'REST / SMALL BREATH / 3 s LOOP'
    if state == 'Cast':
        if t < .2: return 'REST'
        if t < .65: return 'GATHER / LOWER SHOULDERS'
        if t < 2.2: return 'RAISE STAFF / CHANT'
        if t < 2.95: return 'CHARGE HOLD'
        return 'LOWER ARMS / RETURN TO IDLE'
    if state == 'Attack':
        if t < .45: return 'REST'
        if t < .95: return 'GATHER'
        if t < 2.65: return 'RAISE STAFF / CHANT'
        if t < 3.1: return 'CHARGE HOLD'
        if t < 3.65: return 'EXPLOSION RELEASE TO RIGHT / IMPACT 3.50 s'
        if t < 4.4: return 'RECOIL'
        if t < 5.8: return 'FATIGUE / LOWER HEAD + SHOULDERS'
        return 'RECOVER TO IDLE'
    if state == 'Hit':
        if t < .22: return 'SHORT CHEST / SHOULDER RECOIL'
        if t < .42: return 'WRIST + HEAD FOLLOW-THROUGH'
        return 'SETTLE / RECOVER TO IDLE'
    if t < .95: return 'FATIGUE / HEAD + SHOULDERS SINK'
    if t < 1.5: return 'BRIEF EXHAUSTION HOLD'
    return 'RECOVER TO IDLE'


def render(item):
    kind, index = item
    frame = DATA['frames' if kind == 'frame' else 'qa_frames'][index]
    name = frame['state']
    t = frame['state_time']
    order = [s['state'] for s in DATA['segments']]
    im = Image.new('RGB', (W, H), '#090e18')
    d = ImageDraw.Draw(im)
    d.rectangle((32,108,912,884), fill='#101b2b')
    d.rectangle((938,108,1408,884), fill='#142133')
    def text(pos, value, size, color):
        d.text(pos, value, font=ImageFont.truetype(FONT,size), fill=color)
    text((52,25), 'MEGUMIN v6  /  FIVE-STATE MOTION REVIEW', 29, '#f1d5a0')
    text((53,67), 'IDLE  /  CAST  /  ATTACK  /  HIT  /  RELAXED     |     NO DEAD CLIP', 14, '#869cba')
    text((54,119), 'FIXED CAMERA / LARGE VIEW', 14, '#8aa5c4')
    text((959,119), '320 px CHARACTER REFERENCE', 14, '#8aa5c4')
    text((959,152), '30 fps  /  ORIGINAL 1x SPEED', 17, '#e2ce9e')
    text((959,185), f'{order.index(name)+1:02d} / 05   {name.upper()}', 23, '#f4ddae')
    text((959,219), f'{t:.2f} / {frame["state_duration"]:.2f} s', 16, '#9bb1c9')
    for y in range(200,830,80): d.line((54,y,887,y), fill='#172638')
    d.line((54,856,886,856), fill='#3a5067')
    d.line((958,820,1386,820), fill='#40586f')
    origins = [(np.array([445,856]),.42),(np.array([1120,820]),320/1452)]
    for origin, scale in origins:
        for x,y in [(461-608,0),(756-608,-65)]:
            q = origin+np.array([x,y])*scale
            d.line((q[0],q[1]-1,q[0],q[1]+10), fill='#a3bcd2', width=2)
    label = f'{name.upper()}  |  {phase(name,t)}'
    text((53,897), label, 20, '#f4ddae')
    text((1220,899), f'{frame["time"]:.2f} s', 20, '#cedbeb')
    text((53,931), 'Continuous cape phase / Fixed bone lengths + foot anchors / Motion-only review', 12, '#849cbb')
    text((883,931), 'SOFTWARE RASTER OF GODOT GEOMETRY / NOT WINDOW CAPTURE', 11, '#d8b780')
    d.rectangle((53,870,53+1332*min(frame['time']/DATA['duration'],1),874), fill='#d8b780')
    canvas = np.concatenate((np.asarray(im).astype(np.float32)/255., np.ones((H,W,1),np.float32)),axis=2)
    coords = np.fromfile(OUT/frame['file'],dtype='<f4').reshape(-1,2)
    for origin, scale in origins:
        offset=0
        for part in frame['parts']:
            pts=coords[offset:offset+part['count']]
            offset+=part['count']
            raster.raster_part(canvas,part['key'],pts,origin,scale)
    out=Image.fromarray((canvas[:,:,:3]*255).clip(0,255).astype('uint8'))
    path=OUT/Path(frame['file']).with_suffix('.png')
    out.save(path)
    return str(path)


def main():
    keys = [('key', i) for i in range(len(DATA['qa_frames']))]
    items = keys if '--keys-only' in sys.argv else [('frame',i) for i in range(len(DATA['frames']))]+keys
    start=time.time()
    if '--parallel' in sys.argv:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=4) as pool:
            for n,path in enumerate(pool.map(render,items)):
                if n%30==0: print(f'{n+1}/{len(items)} rendered / {time.time()-start:.1f}s / {Path(path).name}',flush=True)
    else:
        for n,item in enumerate(items):
            path=render(item)
            print(f'{n+1}/{len(items)} / {Path(path).name}',flush=True)
    print(f'FIVE_STATE_RASTER_COMPLETE {len(items)} frames / {time.time()-start:.1f}s',flush=True)

if __name__ == '__main__': main()
