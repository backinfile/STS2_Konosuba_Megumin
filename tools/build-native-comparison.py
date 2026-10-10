"""Synchronize/crop already-recorded native videos; never interpolate frames."""
from pathlib import Path
import hashlib,json,subprocess,shutil

root=Path(__file__).resolve().parents[1]/'art/megumin-quartet-spine'
out=root/'actions-v9/verification/recordings'
items=[('chant_enter','Chant entry'),('relaxed_fall','Collapse'),('get_up','Get up'),('dead','Death')]
records=[]
for clip,label in items:
    inputs=[];filters=[];sources=[]
    for i,version in enumerate(('v8','v9')):
        directory=root/f'actions-{version}/verification/recordings'
        source=directory/(clip+'.mp4');metadata=json.loads(source.with_suffix('.json').read_text(encoding='utf-8'))
        key=next(k for k in metadata['timeline'] if k['clip']==clip)
        start=max(0,key['at']-.25);duration=key['seconds']+.6
        inputs+=['-i',str(source)]
        filters.append(f"[{i}:v]trim=start={start}:duration={duration},setpts=PTS-STARTPTS,crop=420:280:150:240,pad=420:316:0:36:color=0x17201b,drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='{version} / {label}':fontcolor=white:fontsize=19:x=16:y=8[v{i}]")
        sources.append({'version':version,'file':str(source.relative_to(root)),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'trim_start':start,'duration':duration})
    target=out/f'compare-{clip}.mp4'
    command=['ffmpeg','-hide_banner','-loglevel','error',*inputs,'-filter_complex',';'.join(filters)+';[v0][v1]hstack=inputs=2:shortest=1[v]','-map','[v]','-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart','-y',str(target)]
    subprocess.run(command,check=True)
    records.append({'clip':clip,'file':target.name,'sources':sources})
listing=out/'comparison-concat.txt'
listing.write_text('\n'.join("file '"+r['file']+"'" for r in records),encoding='utf-8')
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(listing),'-c','copy','-movflags','+faststart','-y',str(out/'v8-v9-comparison.mp4')],check=True)
(out/'comparison.json').write_text(json.dumps({'method':'Original-speed native videos aligned at animation command time, cropped and joined. No optical-flow interpolation or retiming.','clips':records},indent=2),encoding='utf-8')
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>惠惠 v8 / v9 原速对照</title><style>body{max-width:1100px;margin:36px auto;padding:0 24px;background:#eeeae3;color:#2c302b;font:16px/1.6 system-ui}h1{font-size:28px}video,img{display:block;width:100%;background:#17201b}a{color:#216b63}p{max-width:930px}small{color:#666}</style><h1>惠惠 v8 / v9 原速对照</h1><p>左：v8，右：v9。依次为进入吟唱、脱力趴地、撑地起身、死亡。两侧按动作触发时刻对齐，均来自游戏实时录像，仅裁切角色区域并排展示；没有变速或补帧。</p><video controls preload="metadata" src="v8-v9-comparison.mp4"></video><p><a href="index.html">查看 v9 全部 19 个动作与完整战斗</a> · <a href="v8-v9-comparison.mp4" download>下载对照视频</a> · <a href="../../../actions-v8/verification/recordings/index.html">查看 v8 原录像</a></p><h2>改动依据</h2><p>动作总时长不变，经过姿势不再各自减速到零。身体与握点采用连续弧线，并给头、手和披风不同的先后时序。仍保留动作起止和真实停顿；独立角度画稿之间仍可能有轮廓差异。</p><img src="../motion-comparison.png" alt="Spine 实际运行数据的速度和握杖轨迹对照"><p><small>虚线标出本轮五个停顿回归检查点，轨迹点间隔为 0.1 秒。数值来自 Spine Core 4.2.95；曲线通过不替代原速画面验收。</small></p></html>'''
shutil.copyfile(out.parent/'motion-comparison.png',out/'motion-comparison.png')
page=page.replace('../motion-comparison.png','motion-comparison.png')
(out/'comparison.html').write_text(page,encoding='utf-8')
print(out/'comparison.html')
