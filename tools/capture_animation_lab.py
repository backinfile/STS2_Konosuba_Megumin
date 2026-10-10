"""Capture the native game renderer through the project-local test APIs."""
import io,json,time,urllib.request,argparse,os
from pathlib import Path
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
def request(port,path,body=None):
    data=None if body is None else json.dumps(body).encode()
    return urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{port}{path}',data,{'Content-Type':'application/json'}),timeout=20).read()
def capture(clip,t):
    request(15529,'/animation',{'name':clip,'time':t})
    time.sleep(.05)
    request(15529,'/render',{})
    return Image.open(io.BytesIO(request(15528,'/api/v1/screenshot'))).convert('RGB')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--clip',default='chant_enter');p.add_argument('--switches',action='store_true');args=p.parse_args()
    out=ROOT/'art/megumin-quartet-spine'/os.environ.get('MEGUMIN_ACTIONS','actions-v9');raw=json.loads((out/'export/megumin.json').read_text());meta=json.loads((out/'authoring.json').read_text())
    times=[t for t,_ in meta['clips'][args.clip]['schedule']]
    if args.switches:
        times=[max(0,k['time']+dt) for k in raw['animations'][args.clip]['slots']['head']['attachment'] if k['time'] for dt in (-1/60,0,1/60)]
    dest=out/'verification/native';dest.mkdir(parents=True,exist_ok=True)
    sheet=Image.new('RGB',(420*3,300*((len(times)+2)//3)), '#e9e3da');draw=ImageDraw.Draw(sheet)
    for i,t in enumerate(times):
        im=capture(args.clip,t);im.save(dest/f'{args.clip}-{t:.5f}.png')
        im=im.crop((150,240,570,520));x=i%3*420;y=i//3*300
        sheet.paste(im,(x,y+20));draw.text((x+8,y+3),f'{args.clip} @ {t:.5f}s',fill='#312824')
    suffix='switches' if args.switches else 'keys'
    sheet.save(dest/f'{args.clip}-{suffix}.jpg',quality=93)
    print(dest/f'{args.clip}-{suffix}.jpg')
