"""Tie the verified animation, deployed mod, and native recording evidence together."""
from pathlib import Path
import hashlib,json,zipfile

repo=Path(__file__).resolve().parents[1]
art=repo/'art/megumin-quartet-spine/actions-v9'
verification=art/'verification'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=sha(art/'export/megumin.json')
assert source==sha(repo/'dist/MeguminMod/animation/megumin.spine-json')
assert source==sha(repo/'.local/game/mods/MeguminMod/animation/megumin.spine-json')
native=json.loads((verification/'native-lab.json').read_text(encoding='utf-8'))
assert native['passed'] and native['skeleton_sha256']==source and len(native['native_clips'])==19
reports={name:json.loads((verification/name).read_text(encoding='utf-8')) for name in ('continuity.json','motion-rhythm.json','recordings/verification.json')}
assert all(r['passed'] for r in reports.values())
combat=json.loads((verification/'recordings/normal-combat.json').read_text(encoding='utf-8'))
assert combat['end']['state_type']=='rewards' and combat['frame_seeking'] is False
with zipfile.ZipFile(repo/'dist/MeguminMod-0.1.0-dev.zip') as z:
    assert z.testzip() is None
    path=next(n for n in z.namelist() if n.replace('\\','/').endswith('/animation/megumin.spine-json'))
    assert hashlib.sha256(z.read(path)).hexdigest()==source
baseline=sha(repo/'art/megumin-quartet-spine/actions-v8/export/megumin.json')
assert baseline=='15ae6e95f141870bf1588290ae3e4c8de9be1a1ed1641beffeee70870ad75d16'
recordings=reports['recordings/verification.json']['videos']
report={'passed':True,'version':'v9','skeleton_sha256':source,'unchanged_v8_sha256':baseline,
        'native_clips':19,'native_sample_times':57,'normal_combat_actions':len(combat['timeline']),
        'normal_combat_end':combat['end']['state_type'],'native_recordings':len(recordings),
        'minimum_capture_fps':min(r['capture_fps'] for r in recordings),
        'mod_zip_sha256':sha(repo/'dist/MeguminMod-0.1.0-dev.zip'),
        'video_zip_sha256':sha(verification/'recordings/megumin-v9-native-recordings.zip'),
        'limits':['Discrete drawing contours still differ across large angle changes.','Spine Editor import not manually checked.','Gameplay uses placeholder cards and relics.']}
(verification/'delivery.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
