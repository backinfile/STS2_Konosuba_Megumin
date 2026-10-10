"""Exercise the isolated Megumin lab with real game actions and rendering."""
import json,time,hashlib,argparse,os
from pathlib import Path
from capture_animation_lab import request

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'art/megumin-quartet-spine'/os.environ.get('MEGUMIN_ACTIONS','actions-v9')
OUT=ART/'verification'
def get_state():return json.loads(request(15528,'/api/v1/singleplayer?format=json'))
def action(name,**kwargs):
    result=json.loads(request(15528,'/api/v1/singleplayer',{'action':name,**kwargs}))
    assert result.get('status')=='ok',result
    time.sleep(.35)
    return result
def wait_for(predicate,timeout=15):
    end=time.monotonic()+timeout
    while time.monotonic()<end:
        state=get_state()
        if predicate(state):return state
        time.sleep(.15)
    raise AssertionError(f'Timed out: {state}')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--combat',action='store_true');args=parser.parse_args()
    health=json.loads(request(15529,'/health'))
    assert health['character']=='MEGUMINMOD-MEGUMIN'
    assert health['user_data'].replace('\\','/').endswith('/MeguminModLab-STS2_Konosuba_Megumin'),health
    state=get_state()
    if state.get('menu_screen')=='main' and 'continue' in state.get('options',[]):
        action('menu_select',option='continue')
        state=wait_for(lambda s:s.get('battle',{}).get('is_play_phase'))
    assert state.get('battle',{}).get('is_play_phase'),'Enter a test combat before running this script.'
    assert state['player']['character']=='惠惠（测试）'
    raw_path=ART/'export/megumin.json'
    meta=json.loads((raw_path.parents[1]/'authoring.json').read_text())
    report={'game':'0.107.1','character':health['character'],'save_dir':health['user_data'],
            'skeleton_sha256':hashlib.sha256(raw_path.read_bytes()).hexdigest(),'native_clips':[],'actions':[]}
    for clip in health['animations']:
        duration=meta['clips'][clip]['duration']
        for t in [0,duration/2,duration]:
            result=json.loads(request(15529,'/animation',{'name':clip,'time':t}))
            assert result['status']=='ok'
            time.sleep(.025)
            request(15529,'/render',{})
            png=request(15528,'/api/v1/screenshot')
            assert png[:8]==b'\x89PNG\r\n\x1a\n' and len(png)>10000
        report['native_clips'].append(clip)
    request(15529,'/animation',{'name':'idle_loop','loop':True})
    if args.combat:
        start=get_state();report['combat_start']={'hp':start['player']['hp'],'enemies':start['battle']['enemies']}
        for _ in range(80):
            state=wait_for(lambda s:s.get('state_type') not in ('loading','transition'))
            if not state.get('battle'):break
            if not any(e['hp']>0 for e in state['battle']['enemies']):
                wait_for(lambda s:not s.get('battle'))
                break
            if not state['battle'].get('is_play_phase'):
                time.sleep(.3);continue
            cards=[c for c in state['player']['hand'] if c['can_play']]
            attacks=[c for c in cards if c['type']=='Attack']
            if attacks or cards:
                card=(attacks or cards)[0];kw={'card_index':card['index']}
                if card['target_type']=='AnyEnemy':kw['target']=next(e['entity_id'] for e in state['battle']['enemies'] if e['hp']>0)
                result=action('play_card',**kw);report['actions'].append({'card':card['id'],'result':result})
            else:report['actions'].append(action('end_turn'))
        else:raise AssertionError('Combat did not complete within 80 actions')
        report['combat_end']=wait_for(lambda s:s.get('state_type') in ('rewards','card_reward','map','game_over'))
        assert report['combat_end']['state_type'] in ('rewards','card_reward','map'),report['combat_end']
    report['passed']=True
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'native-lab.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'passed':True,'native_clips':len(report['native_clips']),'actions':len(report['actions']),'state':get_state()['state_type']}))
if __name__=='__main__':main()
