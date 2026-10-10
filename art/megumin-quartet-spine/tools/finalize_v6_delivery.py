"""Keep the v6 delivery notes and entry controls aligned with the export."""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
out = root / 'actions-v6'

path = root / 'tools/build_chant_enter_plan.py'
text = path.read_text(encoding='utf-8').replace("'chant_ready → new chant_loop@0'", "'播放状态接入 chant_loop@0；无伤害事件'")
path.write_text(text, encoding='utf-8')

path = root / 'tools/chant_enter_plan.html'
text = path.read_text(encoding='utf-8')
text = text.replace("$('prev').onclick=()=>{playing=false;select(current-1)}", "$('prev').onclick=()=>{playing=false;$('play').textContent='播放';select(current-1)}")
text = text.replace("$('next').onclick=()=>{playing=false;select(current+1)}", "$('next').onclick=()=>{playing=false;$('play').textContent='播放';select(current+1)}")
text = text.replace("$('number').onchange=()=>{playing=false;select(+$('number').value)}", "$('number').onchange=()=>{playing=false;$('play').textContent='播放';select(+$('number').value)}")
text = text.replace("const step=Math.floor(elapsed/(1000/60));select(current+step);", "const step=Math.floor(elapsed/(1000/60)),remainder=elapsed-step*(1000/60);select(current+step);elapsed=remainder;")
path.write_text(text, encoding='utf-8')

(out / 'README.md').write_text('''# 惠惠 · 单手吟唱与趴地脱力 v6

[播放完整动作](preview.html) · [F00–F72 逐帧页](../chant-enter-plan/index.html) · [54 帧过程检查](review-frames.html) · [Spine 导入包](megumin-actions-v6-import.zip)

2026-10-10。根据《整理异世界四重奏惠惠立绘》中的 A03 单手伸杖关系，重新编排进入吟唱，并把脱力及其恢复改为趴地流程。沿用已认可的待机。v5 保留在相邻目录供比较。

交付为 Spine 4.2.11 JSON：25 根骨骼、32 个插槽、18 段动作与一个静态检查片段、13 张图集页。离线预览内嵌 Spine WebGL 4.2.95、纹理与动画数据；打开 `preview.html` 即可播放。

## 本轮动作

- **进入吟唱：1.20 秒，60 fps。** F00–F72 每一帧都有动作指令与数值。顺序为视线先行、落脚转体、握点走低弧、单手前送、缓冲、接入循环。逐帧页直接渲染实际导出的 v6 数据，红线追踪右臂，青线追踪左臂。
- **持杖手一致。** 待机、吟唱、释放、趴下与恢复均由角色自身右手握住原位置；左手在身侧放松，倒下时撑地。角色没有水平镜像，也没有交换眼罩、绷带与左右手归属。
- **转面连续。** 取消 v5 进入动作中整头切换，改用原头身网格连续变形。F08–F35 长杖从头与帽后、躯干前经过；F30 右臂投影共线后再转换肘的可见面。
- **脱力趴下。** 前倾失力、左掌撑地缓冲、胸腹伏下，最终腹部朝地、披风覆背，头靠近前臂。新增趴姿头、躯干和腿部绘图。恢复由左掌先撑起、收腿、站稳、原右手收杖组成。
- **关联动作同步。** 普通攻击、取消吟唱、受击、爆裂卸力、死亡和趴地后死亡均使用对应的新姿势和衔接。

参考为 [A03 官方剧照](https://isekai-quartet.com/assets/story2/3_6.jpg)，出自第 2 季第 3 集。它提供单手持杖的姿态依据，没有提供连续动画帧。时长、过渡和趴地序列是本项目设计。

## 验证

[运行时报告](export/validation.json) 使用实际导出的 Spine 数据采样 **3,353** 个时刻，检查 IK、肢体伸长、可见网格接地、握点、循环与片段衔接，全部通过。四个循环的端点差为 0；14 处衔接的最大差约 0.000023 世界像素。

[关节报告](joint-audit.json) 以 240 Hz 采样 **6,683** 个时刻，肘膝折角、相邻关节位移及弯曲时方向翻转没有越界项。150° 折角、240 Hz 下 3 px 位移是本项目筛查阈值，不是通用生理标准。

已认可的待机逐顶点差约 0.0000153 世界像素，属于浮点误差量级。起身前 0.78 秒左掌保持撑地，漂移约 0.013 px。右手和杖握点一致；一次释放只有一个 `release` 事件。

浏览器复看覆盖六组共 54 个关键时刻，并检查逐帧控件及完整播放流程。数值检查不能代替美术判断；趴姿转换仍使用专用绘图，肩袖与衣片的局部轮廓仍可继续精修。

## 片段时长

| 片段 | 秒 | 后续 / 事件 |
|---|---:|---|
| `idle_loop` | 4.00 循环 | 待机 |
| `cast_short` | 0.70 | 待机 |
| `chant_enter` | 1.20 | 单手吟唱 |
| `chant_loop` | 2.00 循环 | 等待释放 |
| `chant_cancel` | 1.20 | 原路线收杖回待机 |
| `chant_ack` | 0.50 | 吟唱 |
| `attack_short` | 1.38 | 0.68 秒 `impact`，随后待机 |
| `explosion_release` | 0.68 | 0.46 秒唯一 `release` |
| `explosion_hold` | 0.60 循环 | 等待多段伤害结算完毕 |
| `explosion_exit` | 0.65 | 前倾失力 |
| `hit` / `hit_chant` | 0.44 | 回到各自原状态 |
| `relaxed_fall` | 1.30 | 趴地保持 |
| `relaxed_loop` | 3.00 循环 | 等待恢复 |
| `get_up` | 3.10 | 从趴地撑起回待机 |
| `dead` | 1.80 | 最后一帧保持 |
| `dead_from_down` | 0.45 | 死亡保持 |
| `hit_down` | 0.30 | 趴地保持 |
| `setup_pose` | 4.00 | 静态检查 |

演示模拟三次伤害脉冲，身体只释放一次；并未执行游戏伤害。正式接入应由玩法事件控制状态，不能按每个敌人或每次伤害重播释放。F72 接入吟唱是状态转换，没有新增 `chant_ready` Spine 事件。

## 美术与导入

本轮新增的 [趴姿分件原图](source/prone-parts.png) 使用内置 image_gen 生成，[完整提示词](source/prone-parts-prompt.txt) 已保存。其余绘图继承前版，原图、提示词和分区都保留在 `source/`，源图哈希记录在 `export/manifest.json`。

脚本只做 UV 网格、蒙皮、时间线和原像素装箱，没有用代码重绘源图。接地与转面已烘焙到标准 Spine 数据，无需额外的游戏运行时修正脚本。

在 Spine 4.2 中通过 Import Data 选择 `export/megumin.json`，图片路径为 `../images/`。运行时使用 JSON 或同内容 `.spine-json`、atlas 及 13 张图集 PNG，并保留 mipmap 过滤。ZIP 同时包含原图、提示词、验证报告和逐帧 JSON/CSV。

尚未在原生 Spine 编辑器或 STS2 游戏内验证。本版是二维网格动作样机，没有提供 `.spine` 工程或 `.skel` 二进制文件。

## 复现

在上级 `art/megumin-quartet-spine` 目录运行：

```powershell
npm run build:actions:v6
npm run test:actions:v6
```

构建顺序：逐帧规划 → v6 骨架/动作 → 接地烘焙 → 转面烘焙 → 运行时与关节检查 → 预览/ZIP → 关键帧页面 → 逐帧页面。转面烘焙必须在接地烘焙后运行，保留已有接地变形。构建需要本项目已有的 Node、Python、Pillow 与几何依赖。
''', encoding='utf-8')

path = root / 'README.md'
text = path.read_text(encoding='utf-8')
start = text.index('**最新动作修正：')
end = text.index('\n\n2026-10-09。',start)
text = text[:start] + '''**最新动作修正：[Actions v6 交互预览](actions-v6/preview.html) · [F00–F72 逐帧页](chant-enter-plan/index.html) · [54 帧复查](actions-v6/review-frames.html) · [制作说明](actions-v6/README.md)**。根据四重奏 A03 的单手关系重新编排进入吟唱，始终由原右手握杖；脱力改为胸腹朝地，并连同撑起、受击和死亡分支更新。

[Idle v2](idle-v2/preview.html) 保留为静态基准；[v3 审查](actions-v3/action-audit.html)、[v4](actions-v4/preview.html)、[v5](actions-v5/preview.html) 保留供比较。最新数据在 `actions-v6/export/`。下文是历史 v1 样机记录。''' + text[end:]
path.write_text(text, encoding='utf-8')
path = root / 'index.html'
text = path.read_text(encoding='utf-8').replace('actions-v5/preview.html','actions-v6/preview.html').replace('查看侧身单手伸杖与关节修正版 v5 →','查看同手吟唱与趴地脱力修正版 v6 →')
path.write_text(text, encoding='utf-8')
print('v6 delivery notes and controls aligned')
