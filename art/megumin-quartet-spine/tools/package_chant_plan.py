from pathlib import Path
import json,base64,shutil
root=Path(__file__).resolve().parents[1];out=root/'chant-enter-plan';v6=root/'actions-v6'
plan=json.loads((out/'frame-plan.json').read_text(encoding='utf-8'))
plan['status']='Implemented in v6; numerical targets plus the exact exported animation preview.'
plan['reference']='Isekai Quartet S2 E3 official still A03; static pose, not a continuous animation sequence.'
plan['hand_identity']='Character anatomical right arm, inherited from approved standing image, continuously owns the original staff grip.'
# Keep instructions aligned with the final near hip position of the free hand.
for p in plan['frames']:
    p['note']=p['note'].replace('左臂开始向后让位','左臂放松下垂让位').replace('左手继续向后下方放松','左手继续在髋旁放松').replace('左肩后收','左肩随躯干转面').replace('左手接近放松终点','左手在髋旁接近放松终点')
    p['layer']='杖在头/帽后、躯干前；右手始终持杖' if p['staff_behind_head'] else '右臂和杖在躯干前；左手在髋旁放松'
packed={'plan':plan,'poses':json.loads((v6/'authoring-poses.json').read_text(encoding='utf-8'))['chant_enter'],'validation':json.loads((v6/'export/validation.json').read_text(encoding='utf-8')),'skeleton':json.loads((v6/'export/megumin.json').read_text(encoding='utf-8')),'atlas':(v6/'export/megumin.atlas').read_text(encoding='utf-8'),'pages':{f.name:'data:image/png;base64,'+base64.b64encode(f.read_bytes()).decode('ascii') for f in (v6/'export').glob('*.png')}}
ref='data:image/jpeg;base64,'+base64.b64encode((root.parent/'isekai-quartet-references-20261009/originals/A03-s2-e03-6.jpg').read_bytes()).decode('ascii')
html=(root/'tools/chant_enter_plan.html').read_text(encoding='utf-8').replace('__DATA__',json.dumps(packed,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')).replace('__REF__',ref).replace('__RUNTIME__',(root/'vendor/spine-webgl-4.2.95.min.js').read_text(encoding='utf-8'))
(out/'index.html').write_text(html,encoding='utf-8')
(out/'implemented-frame-plan.json').write_text(json.dumps({'plan':plan,'actualAuthoringPoses':packed['poses'],'validation':packed['validation']},ensure_ascii=False,indent=2),encoding='utf-8')
dest=Path.home()/'.agent/diagrams/megumin-chant-enter-frame-plan.html';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(out/'index.html',dest)
print('Frame plan: 73 samples / actual v6 Spine /',len(html),'characters')
