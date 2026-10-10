"""Record normal-speed native game animation playback, not frozen frame synthesis."""
import argparse,hashlib,json,shutil,time,subprocess,os
from pathlib import Path
from capture_animation_lab import request

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'art/megumin-quartet-spine'/os.environ.get('MEGUMIN_ACTIONS','actions-v9')
OUT=ART/'verification/recordings'
def api(port,path,body=None):return json.loads(request(port,path,body))
def play(name,loop=False):return api(15529,'/animation',{'name':name,'loop':loop})
def wait_recording():
    for _ in range(100):
        state=api(15528,'/api/v1/recording')
        if state['status'] not in ('recording','stopping'):
            assert state['status']=='completed',state
            return state
        time.sleep(.2)
    raise RuntimeError('Recording finalization timed out')

def record(name,sequence):
    OUT.mkdir(parents=True,exist_ok=True)
    play(sequence[0][0],sequence[0][2]);api(15529,'/render',{})
    time.sleep(.15)
    api(15528,'/api/v1/recording/start',{'fps':30,'width':1280,'height':720,'max_duration_seconds':int(sum(s[1] for s in sequence))+5,'audio':False})
    start=time.monotonic();timeline=[]
    try:
        for clip,duration,loop in sequence:
            play(clip,loop)
            timeline.append({'clip':clip,'at':round(time.monotonic()-start,4),'seconds':duration,'loop':loop})
            time.sleep(duration)
    finally:api(15528,'/api/v1/recording/stop',{})
    state=wait_recording();target=OUT/(name+'.mp4');shutil.copyfile(state['output_path'],target)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(target)],text=True))
    result={'name':name,'file':target.name,'source':'live native game viewport','playback_rate':1,'frame_seeking':False,
            'timeline':timeline,'capture':state,'probe':probe,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
    (OUT/(name+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'recorded':name,'seconds':state['video_duration_seconds'],'capture_fps':state['capture_fps'],'repeated_frames':state['frames_repeated']}),flush=True)
    return result

def plans(meta):
    duration=lambda n:meta['clips'][n]['duration']
    idle=('idle_loop',1.2,True);chant=('chant_loop',1.2,True);down=('relaxed_loop',1.2,True)
    out={}
    for name,p in meta['clips'].items():
        if name.startswith('_bind/'):continue
        if p['loop']:out[name]=[(name,max(4,p['duration']*2),True)];continue
        before,after=idle,idle
        if name in ['chant_ack','chant_cancel','explosion_release','hit_chant']:before=chant
        if name in ['chant_enter','chant_ack','hit_chant']:after=chant
        if name=='explosion_release':after=('explosion_hold',1.4,True)
        if name=='explosion_exit':before=('explosion_hold',1.4,True);after=('relaxed_fall',duration('relaxed_fall'),False)
        if name=='relaxed_fall':before=('explosion_exit',duration('explosion_exit'),False);after=down
        if name in ['get_up','hit_down','dead_from_down']:before=down
        if name=='hit_down':after=down
        if name in ['dead','dead_from_down']:after=('dead_loop',1.5,True)
        out[name]=[before,(name,p['duration'],False),after]
    out['full-sequence']=[('idle_loop',2,True),('chant_enter',duration('chant_enter'),False),('chant_loop',2.4,True),('chant_ack',duration('chant_ack'),False),('chant_loop',2.4,True),('explosion_release',duration('explosion_release'),False),('explosion_hold',1.4,True),('explosion_exit',duration('explosion_exit'),False),('relaxed_fall',duration('relaxed_fall'),False),('relaxed_loop',3,True),('get_up',duration('get_up'),False),('idle_loop',2,True)]
    return out

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--only');args=parser.parse_args()
    meta=json.loads((ART/'authoring.json').read_text(encoding='utf-8'))
    exported=hashlib.sha256((ART/'export/megumin.json').read_bytes()).hexdigest()
    installed=hashlib.sha256((ROOT/'.local/game/mods/MeguminMod/animation/megumin.spine-json').read_bytes()).hexdigest()
    assert exported==installed,'Build and restart the lab with the selected animation version before recording.'
    selected=plans(meta)
    if args.only:selected={args.only:selected[args.only]}
    assert api(15529,'/health')['native_spine'],'Enter a Megumin combat first'
    assert api(15528,'/api/v1/singleplayer?format=json').get('battle',{}).get('is_play_phase'),'Wait until the combat is ready'
    time.sleep(2)
    results=[record(name,sequence) for name,sequence in selected.items()]
    play('idle_loop',True)
    (OUT/'index.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
