from pathlib import Path
import json
root=Path(__file__).resolve().parents[1];out=root/'actions-v6'
file=out/'preview.js';text=file.read_text(encoding='utf-8')
for a,b in {
 '转为侧身，右手单手向前伸杖，左臂向后展开。':'原持杖右手走低弧前送；头身连续转向，左手始终放松。',
 '保持侧身、单手前伸杖；等待游戏的释放事件。':'保持三分之四侧身与单手前伸；等待游戏的释放事件。',
 '抬杖短送，杖头全程可见，结束返回待机。':'沿相同握点前送；杖从头部后侧经过，结束返回待机。',
 '腿软后坐倒，再向后躺下；同一套骨架连续过渡。':'前倾失力，左掌撑地，再伏低胸腹，趴在前臂旁。',
 '仰躺微呼吸，不自动视为死亡。':'腹部朝地，披风覆背，头靠近前臂；轻微呼吸。',
 '左掌撑地，收腿承重，再握杖、起身恢复原姿。':'左掌固定撑起，收腿站稳，再沿同一路径收杖；右手不换握。',
 '侧倒后保持最后一帧。':'前扑失力后保持最后一帧。',
 "shadowX=mode==='down'||mode==='dead'?-50:0":"shadowX=mode==='down'||mode==='dead'?65:0"
}.items():text=text.replace(a,b)
file.write_text(text,encoding='utf-8')
file=out/'index.html';text=file.read_text(encoding='utf-8').replace('Spine v5','Spine v6').replace('侧身单手伸杖 · 修正肘膝弯折','全程同一只手持杖 · 前倾趴地脱力').replace('右手单持 · 侧身前伸 · 连续肘膝轨迹','右手始终持杖 · 连续转身 · 趴地与撑起')
if '进入吟唱逐帧表' not in text:text=text.replace('九帧动作对照</a>','九帧动作对照</a> · <a href="../chant-enter-plan/index.html">进入吟唱逐帧表</a>')
file.write_text(text,encoding='utf-8')
file=root/'tools/gallery_actions_v6.py';text=file.read_text(encoding='utf-8').replace('坐倒过渡','左掌撑地').replace('仰躺脱力','趴地脱力').replace("['死亡保持','dead',1.5]","['死亡保持','dead',1.8]").replace("?-20:20","?55:25")
file.write_text(text,encoding='utf-8')
file=root/'tools/build_review_v6.py';text=file.read_text(encoding='utf-8')
start=text.index('groups=[');end=text.index('\nhtml=',start)
groups=[
 ('待机与手势',[('待机','idle_loop',0),('张掌','cast_short',.12),('普通施放','cast_short',.28),('收手','cast_short',.5),('受击','hit',.035),('受击冲量','hit',.07),('帽发','hit',.13),('回收','hit',.27),('原姿','hit',.44)]),
 ('吟唱逐帧关键点',[('F00 原手持杖','chant_enter',0),('F06 视线先行','chant_enter',.1),('F12 杖过头后','chant_enter',.2),('F20 落脚','chant_enter',20/60),('F24 低位前送','chant_enter',.4),('F30 肘尖换面','chant_enter',.5),('F42 前送','chant_enter',.7),('F58 缓冲','chant_enter',58/60),('F72 吟唱入口','chant_enter',1.2)]),
 ('释放与卸力',[('出招准备','attack_short',.2),('出招','attack_short',.68),('出招收回','attack_short',1.1),('爆裂蓄力','explosion_release',.15),('爆裂收蓄','explosion_release',.28),('一次释放','explosion_release',.46),('保持','explosion_hold',0),('卸力','explosion_exit',.32),('失力','explosion_exit',.65)]),
 ('趴下全过程',[('失力','relaxed_fall',0),('前倾','relaxed_fall',.18),('伸掌','relaxed_fall',.34),('撑地','relaxed_fall',.48),('手臂缓冲','relaxed_fall',.75),('伏低','relaxed_fall',.90),('胸腹朝地','relaxed_fall',1.02),('趴地','relaxed_fall',1.16),('趴地保持','relaxed_loop',0)]),
 ('从趴地撑起',[('趴地起点','get_up',0),('左掌固定','get_up',.38),('上身撑起','get_up',.65),('收腿','get_up',.78),('抬左手','get_up',1.03),('站起','get_up',1.42),('重新站稳','get_up',1.9),('原右手收杖','get_up',2.6),('原待机','get_up',3.1)]),
 ('受击与死亡',[('吟唱受击','hit_chant',.1),('吟唱恢复','hit_chant',.44),('趴地受击','hit_down',.15),('死亡失力','dead',.38),('死亡撑地','dead',1.05),('死亡伏低','dead',1.45),('死亡保持','dead',1.8),('趴地后死亡','dead_from_down',.22),('最终保持','dead_from_down',.45)])
]
text=text[:start]+'groups='+repr(groups)+text[end:];file.write_text(text,encoding='utf-8')
file=root/'package.json';obj=json.loads(file.read_text(encoding='utf-8'));obj['scripts']['build:actions:v6']='py -X utf8 tools/build_chant_enter_plan.py && py -X utf8 tools/build_actions_v6.py && node tools/bake_floor_v6.mjs && node tools/bake_turn_v6.mjs && node tools/validate_actions_v6.mjs && node tools/audit_joint_logic.mjs actions-v6 --strict && py -X utf8 tools/package_actions_v6.py && py -X utf8 tools/build_review_v6.py && py -X utf8 tools/package_chant_plan.py';obj['scripts']['test:actions:v6']='node tools/validate_actions_v6.mjs && node tools/audit_joint_logic.mjs actions-v6 --strict';file.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Updated v6 copy and review poses')
