"""Record actual card, enemy-turn, hit and victory playback at normal game speed."""
import json,time,hashlib,shutil,subprocess,os
from pathlib import Path
from capture_animation_lab import request

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'art/megumin-quartet-spine'/os.environ.get('MEGUMIN_ACTIONS','actions-v9')/'verification/recordings'
def api(port,path,body=None):return json.loads(request(port,path,body))
def state():return api(15528,'/api/v1/singleplayer?format=json')
def action(name,**kw):return api(15528,'/api/v1/singleplayer',{'action':name,**kw})

if __name__=='__main__':
    start=state();assert start.get('battle',{}).get('is_play_phase'),'Enter a test combat first'
    api(15529,'/animation',{'name':'idle_loop','loop':True});api(15529,'/render',{})
    api(15528,'/api/v1/recording/start',{'fps':30,'width':1280,'height':720,'max_duration_seconds':180,'audio':False})
    began=time.monotonic();timeline=[];defended=False
    try:
        time.sleep(2)
        for _ in range(140):
            s=state()
            if s.get('state_type') in ('rewards','card_reward','map','game_over'):break
            if not s.get('battle',{}).get('is_play_phase'):
                time.sleep(.3);continue
            enemies=[e for e in s['battle']['enemies'] if e['hp']>0]
            if not enemies:time.sleep(.3);continue
            cards=[c for c in s['player']['hand'] if c['can_play']]
            attacks=[c for c in cards if c['type']=='Attack']
            defense=[c for c in cards if c['id']=='DEFEND_IRONCLAD']
            choice=(defense if not defended and defense else attacks or cards)
            if choice:
                c=choice[0];kw={'card_index':c['index']}
                if c['target_type']=='AnyEnemy':kw['target']=enemies[0]['entity_id']
                result=action('play_card',**kw)
                if c['id']=='DEFEND_IRONCLAD':defended=True
                entry={'action':'play_card','card':c['id'],'result':result}
            else:entry={'action':'end_turn','result':action('end_turn')}
            assert entry['result'].get('status')=='ok',entry
            entry['at']=round(time.monotonic()-began,3);timeline.append(entry)
            print(json.dumps(entry,ensure_ascii=False),flush=True)
            time.sleep(1.8)
        else:raise RuntimeError('Combat did not complete')
        assert s['state_type'] in ('rewards','card_reward','map'),s
        time.sleep(3)
    finally:api(15528,'/api/v1/recording/stop',{})
    for _ in range(100):
        capture=api(15528,'/api/v1/recording')
        if capture['status'] not in ('recording','stopping'):break
        time.sleep(.2)
    assert capture['status']=='completed',capture
    target=OUT/'normal-combat.mp4';shutil.copyfile(capture['output_path'],target)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(target)],text=True))
    result={'name':'normal-combat','file':target.name,'source':'normal card and turn actions in the live game; no animation commands during combat',
            'playback_rate':1,'frame_seeking':False,'start':start,'end':s,'timeline':timeline,'capture':capture,'probe':probe,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
    (OUT/'normal-combat.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'recorded':'normal-combat','seconds':capture['video_duration_seconds'],'actions':len(timeline),'end':s['state_type']}))
