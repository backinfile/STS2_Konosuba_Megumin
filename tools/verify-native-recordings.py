"""Check encoded live recordings for actual moving, visible game frames."""
from pathlib import Path
import argparse,json,subprocess,os
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'art/megumin-quartet-spine'/os.environ.get('MEGUMIN_ACTIONS','actions-v9')/'verification/recordings'
def verify(path):
    data=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-vf','fps=5,crop=420:280:160:230,scale=210:140','-f','rawvideo','-pix_fmt','gray','-'])
    frames=np.frombuffer(data,dtype=np.uint8).reshape(-1,140,210)
    diff=np.abs(np.diff(frames.astype(np.float32),axis=0)).mean(axis=(1,2))
    unique=len({frame.tobytes() for frame in frames})
    bright=(frames>80).mean(axis=(1,2))
    metadata=json.loads(path.with_suffix('.json').read_text(encoding='utf-8'))
    capture=metadata['capture']
    result={'file':path.name,'sampled_frames':len(frames),'unique_character_crops':unique,
            'max_crop_change':float(diff.max(initial=0)),'maximum_visible_bright_fraction':float(bright.max(initial=0)),
            'capture_fps':capture['capture_fps'],'repeated_frames':capture['frames_repeated'],
            'frames_written':capture['frames_written'],'duration':capture['video_duration_seconds']}
    assert capture['status']=='completed' and capture['capture_fps']>=27,result
    assert result['maximum_visible_bright_fraction']>.03,('Blank or stale scene',result)
    if path.stem!='dead_loop':assert unique>=3 and result['max_crop_change']>.01,('No animation motion',result)
    result['passed']=True
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--only');args=p.parse_args()
    allowed=set(json.loads((OUT.parents[1]/'authoring.json').read_text())['clips'])|{'full-sequence','normal-combat'}
    files=[OUT/(args.only+'.mp4')] if args.only else sorted(p for p in OUT.glob('*.mp4') if p.stem in allowed)
    results=[verify(path) for path in files]
    report={'passed':True,'sampling':'5 fps native game character crop; no frame interpolation','videos':results}
    (OUT/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
