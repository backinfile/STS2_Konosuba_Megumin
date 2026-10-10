# 惠惠v9 Spine动画问题与原版对照审查

日期：2026-10-10
审查版本：`23d31cc4d17c0102f37aba65a650a29868e2556f`，默认生产资源 `actions-v9`。

> 版本基线：本报告仅针对上述固定提交，后续资产与代码变更需重新核验。随仓库的统计、四张重点图和外部审计归档的区分见 [资料索引](README.md)；正文其余图名和旧脚本名是外部归档标识，不是未声明的仓库文件。

## 结论和修复顺序

1. **先修片段内部的可见破损**：get_up约0.95–1.05秒胸腰轮廓割裂；relaxed_fall约0.70–0.80秒披风和衣料拉出细尖片。仓库原生录像与独立纹理重建都能复现症状。get_up不能仅凭这些画面归因为三角翻面；需要检查错峰换图期间的身体、披风与手臂覆盖。
2. **同步普通攻击与伤害节拍**：资产impact在0.76秒，现有继承等待0.15秒，名义差0.61秒。源码证据明确，但不是本次实机测得的伤害延迟。
3. **再接完整状态图与打断策略**：19动作已经存在，生产只接六个通用状态；趴地受击/死亡、起身和爆裂链未通过真实状态图完整路由。正式玩法本来声明未完成，不应把未承诺的功能包装为已交付缺陷。
4. **匹配换图边界**：get_up约1.60秒后腿由跪弯投影直接切成平踏，需对齐脚底与膝盖路径。原版也使用离散换图，不能仅因存在切图就判错。
5. **最后润色与优化**：attack_short/cast_short视觉时间轴相同；待机二级运动偏弱；大量常量烘焙帧、18页图集值得压缩。尚无资源引发卡顿的实测证据。

独立验证同时确认：**17条设计端点接续和5个循环首尾逐顶点一致，权重归一正常，idle脚底稳定**。目前最显著的视觉缺陷发生在片段内部，而不是“所有动画首尾都接不上”。端点通过不能替代中途打断、混合与实战节拍验证。

原审查阶段只读取仓库、审阅提交录像、用官方runtime和独立脚本采样重建，未修改mod、推送或重新启动游戏；本次仅将研究成果归档提交。以下详细分为视觉、结构和运行时三个部分。


## 视觉证据与全部19动作台账


### 范围与方法

固定提交：`23d31cc4d17c0102f37aba65a650a29868e2556f`。当前目标是 `art/megumin-quartet-spine/actions-v9/export/megumin.json`，不是历史 v6。独立看过全部 19 个公开动作的录像抽帧接触表；每个动作抽取前态、约 11 个动作内时刻和后态。对 chant_enter、relaxed_fall、get_up、dead 再抽取替换边界的连续 30 fps 帧。

录像来源是仓库 `actions-v9/verification/recordings/*.mp4`，配套 JSON 自述为 live native game viewport；本次确实读取了这些像素，但没有重新启动游戏。录像时间精确到帧（1/30秒）；表内 clip 时间是视频帧时间减 JSON 记录的触发时刻，存在录制/调度相位差，不宜作为精确附件边界。确定附件边界用资产 JSON + 官方 Spine 4.2 runtime 独立求值。

关键点又用官方 `@esotericsoftware/spine-core` / `spine-webgl` 4.2.120 与自行编写 CPU 栅格器重建。未执行仓库脚本，未修改游戏/源资产。重建从 setup pose 开始，动画权重1，无 AnimationState 混合、Godot 外部特效。普通接触表每格单独适配，不用于比较跨帧缩放/位置；`*_fixed.png` 使用相同世界边界、同一比例。CPU 重建用于交叉核验；最终故障认定同时有原生录像支持，避免把自制渲染差异当游戏缺陷。

### 先说结论

v9 已经采用独立站姿、转身、施法、蹲下、支撑、趴下、跪起图，并有分 slot 的错峰替换。这一方向与原版的局部换面和分阶段交接一致；“惠惠还在用一张站姿图强行拉成躺姿”已不适用。

当前最可信的视觉问题是**中间姿态衣料/躯干轮廓破碎、部分替换点的腿部投影跳变**，而不是动作缺失或完全不能播。其次是**不同战斗语义共用过近的轮廓与节奏**，后者属于动画表现判断，不应写成渲染错误。

### A. 已由两种画面证据确认的缺陷

#### A1. get_up：跪起交接时，胸腹出现断裂轮廓和背景孔洞

- 资产精确点：`0.9400 → 0.9501 → 1.0000 s`。0.95s `body` 从 brace/body 切为 kneel-rise/body；head 到1.08333s才切，腿又在1.11667/1.21667s分批切。
- 像素：0.9400s尚为连贯的前倾支撑姿态；0.9501/1.0000s，肩后到腰之间出现割裂的红黄细片、身体内部露出背景的空缺。并非只有衣服花纹改变。到1.2168s整套跪起姿态较完整。
- 原生录像：get_up.mp4 的2.200–2.267s（clip估计0.978–1.045s），相同位置能看到破碎红黄轮廓。2.300s附近朝较完整跪起姿态交接。
- 图证：[contact_sheets/get_up_focus_fixed.png](figures/contact_sheets/get_up_focus_fixed.png) 前两行；`boundaries/get_up.jpg` 第2–3行；原生单帧 [boundaries/get_up_0067.png](figures/boundaries/get_up_0067.png)（视频2.2333s）。
- 判断：高置信视觉缺陷。具体哪个网格权重/三角形导致空缺仍应由结构统计定位，不能仅凭像素断言引擎故障。
- 原版对照：Necrobinder die 虽也分批换图（1.0333接入、1.1000撤旧、1.1667清手臂），但分批的目的应是保住可见的完整躯干/衣料。惠惠这里说明“分批”本身不是质量保证。先把交接前后胸腰覆盖与轮廓对齐，再决定切点，不能只最小化单 slot 三角形代价。

#### A2. relaxed_fall：趴下前，披风/腰后缘拉出不属于正常轮廓的细尖片

- 资产精确点：0.7000/0.7500/0.7999s逐步出现；0.8001s进入 lower 后大幅消失。
- 像素：0.75与0.7999s，披风黄边后端被拉长分叉，背腰区域出现细碎黄/红片与缺口；0.8001s身体和披风突然恢复为完整的趴下过渡画法。
- 原生录像：relaxed_fall.mp4 视频1.367–1.433s（clip估计0.720–0.786s）；视频1.467s为更干净的 lower 轮廓。
- 图证：`contact_sheets/fall_focus.png`、[contact_sheets/fall_focus_fixed.png](figures/contact_sheets/fall_focus_fixed.png)；`boundaries/relaxed_fall.jpg` 第5行；[boundaries/relaxed_fall_0042.png](figures/boundaries/relaxed_fall_0042.png)（视频1.4000s）。
- 判断：高置信局部拉折/轮廓缺陷；可见尖片有原生录像支持，不是仅凭三角形反转计数或 CPU 栅格器作判断。
- 原版对照：Silent 的披风换面、Ironclad 的攻击身体都让图片承担适合它的投影。惠惠此区间应提前换合适姿态，或补一张 brace→lower 中间覆盖图/局部披风，避免让旧图被拉到已经不适用的形状。无需因此整套重建或盲目增加全身骨骼。

#### A3. get_up：1.6000s 后腿轮廓在单次替换中直接从跪弯变平踏

- 资产边界：`1.5999 → 1.6001s`。同机位固定比例重建里，缠绷带腿由膝弯/靴子回卷轮廓直接切成斜直腿、脚底平放；另一腿与衣服轮廓也同刻调整。
- 原生录像：get_up.mp4 视频2.800→2.833s（clip估计1.578→1.611s）能看到同样的两姿态交接。
- 图证：[contact_sheets/get_up_focus_fixed.png](figures/contact_sheets/get_up_focus_fixed.png) 最后一行最后两格；`boundaries/get_up.jpg` 第5行。
- 判断：中置信/中等优先级的接触和投影匹配问题。离散换图本来合法，原版 Silent/Ironclad死亡也能逐帧识别切图；这里不能仅因存在切图就判错。值得修的是脚底着地形状和膝盖轨迹几乎在一个切点完成，没有与前一张图充分对齐。
- 验收建议：固定地面基准，把支撑脚靴底和膝盖投影画在边界前后同一张叠图上；若脚底要落地，用明确的小段动作表达，而不是依赖一次图形替换完成。

### B. 画面可见，但属于动作语义/美术判断

#### B1. attack_short 与 cast_short 很难从角色动作本身区分

两个录像均为竖杖待机→转向→斜举指向→回待机，约0.3–1.0s主轮廓几乎一致。画面重点是摆到施法 pose；缺少不同的攻击方向、打击极值或收势特征。是否需要区别取决于设计：若两者确实只是通用出牌动作，这不构成错误；若分别代表近战打击与魔法，则值得分别设计。

图证：`video_sheets/attack_short.jpg`、`cast_short.jpg`。对照原版 Ironclad attack 0.1000→0.1667 的躯干换面与挥剑极值，或 Necrobinder 的伸袖/手背/镰刀轨迹，关键不是照搬大挥击，而是让预备、事件、收势的轮廓与语义可读。

#### B2. explosion_release 的身体演出相对克制，hold 与 chant 的区别主要在表情/披风

release clip约0.34–0.71s可见张口、略前倾和披风变化，杖与下盘变化不大。可以批评“仅看身体，最终爆发辨识度较弱”，不能说没有动作，也不能凭这段孤立测试录像宣布爆炸特效失效。应与实际特效、声音、命中时机一起判断。若大部分冲击由 VFX 承担，克制的身体姿势也可能是有意设计。

图证：`video_sheets/explosion_release.jpg`、`explosion_hold.jpg`、`chant_loop.jpg`。

#### B3. relaxed_loop 与 dead_loop 的主轮廓/闭眼趴姿几乎相同

两者都脸朝地、闭眼，手杖横放，帽子与四肢布局相同。dead_from_down 测试中几乎没有可见末次松脱/终止动作。这对“耗尽魔力暂时趴下”和“死亡”是辨识度问题，但不是状态机故障；游戏生命条、UI及后续能否起身会提供额外语义。

图证：`video_sheets/relaxed_loop.jpg`、`dead_from_down.jpg`、`dead_loop.jpg`。原版可借鉴不同终末轮廓或最终停稳，但没必要强迫可爱风角色解体或消失。很小的头/手最终松脱、握杖变化或呼吸停住即可提供差异。

#### B4. 站立转身缺少清晰的抬脚换重心

chant_enter clip约0.48–0.78s从窄站姿过渡到较宽施法站姿，录像中靴子主要贴近地面改变位置，抬脚感弱。可称“略有滑步观感”，不宜仅凭骨骼位移判定 foot sliding bug：Q版角色转脚、透视变化也会改变图像脚形。先结合脚底接触标记与真实时间播放决定优先级，低于A1/A2。

### C. 全19动作检查台账

| 动作 | 画面复核结果 | 证据 |
|---|---|---|
| idle_loop | 待机稳定、披风/身体动幅很小；不能据缩略表说完全无呼吸 | video_sheets/idle_loop.jpg |
| chant_enter | 转身与举杖可读；前臂投影变短符合转向，不单以9倍长度比例判破骨；有滑步观感待标记核验 | video_sheets/chant_enter.jpg；boundaries/chant_enter.jpg |
| chant_loop | 固定斜举杖轮廓，披风微动；吟唱张力较弱是表现偏好 | video_sheets/chant_loop.jpg |
| chant_cancel | 从斜杖返回竖杖，整体路径连贯；未在所查帧见空白/整身消失 | video_sheets/chant_cancel.jpg |
| chant_ack | 动幅很小，与吟唱待机难一眼区分；确认动作可刻意轻 | video_sheets/chant_ack.jpg |
| explosion_release | 张口/前倾/披风变化可见；爆发力度评价需连同VFX | video_sheets/explosion_release.jpg |
| explosion_hold | 持续伸杖张口，可作为特效持续承载姿态 | video_sheets/explosion_hold.jpg |
| explosion_exit | 表情疲惫、手杖降低、身体前倾，语义清晰 | video_sheets/explosion_exit.jpg |
| relaxed_fall | 有蹲→手支撑→趴地序列；0.70–0.80附近存在已确认轮廓破碎 | video_sheets/relaxed_fall.jpg；fall_focus_fixed.png |
| relaxed_loop | 趴地静态轮廓清晰，与死亡轮廓过近 | video_sheets/relaxed_loop.jpg |
| get_up | 支撑→跪起→站立→收杖流程完整；0.95–1.08躯干破碎，1.60腿投影跳变 | video_sheets/get_up.jpg；get_up_focus_fixed.png |
| hit | 约0.11–0.31s有低幅全身回弹；表情变化弱，属于反馈力度建议 | video_sheets/hit.jpg |
| hit_chant | 保留施法姿态受击，无不必要回待机；幅度克制 | video_sheets/hit_chant.jpg |
| hit_down | 趴姿有短暂移动/压低后回稳，没有站起错误 | video_sheets/hit_down.jpg |
| dead | 站立→前倾→蹲/跪→趴下可读；中段衣料与fall相同区域值得一起修 | video_sheets/dead.jpg；boundaries/dead.jpg |
| dead_from_down | 趴姿几乎不变，技术可行但终末语义弱 | video_sheets/dead_from_down.jpg |
| dead_loop | 稳定趴姿；未见循环跳到站立 | video_sheets/dead_loop.jpg |
| attack_short | 与cast_short同类摆杖语汇，若要表达不同攻击需再区分 | video_sheets/attack_short.jpg |
| cast_short | 同上，所查帧没有整身消失或明显断杖 | video_sheets/cast_short.jpg |

上述“未见”只限本次抽帧与重点区间，不能替代每个实战打断组合的测试。

### 不应误报的项目

- 不能用原始9.63倍的前臂投影距离直接认定肢体拉坏。chant_enter 0.275s转向时手臂近乎朝镜头/被躯干和杖遮挡，约0.6167s伸向侧面，这本来会有大的二维投影长度差。重点应看关节轮廓与接合，不是长度比阈值。
- 本次没有在重点帧确认“手完全脱离握点/杖穿帮”这一独立结论；不要为了列全问题而编造。趴下手部支撑与杖的关系仍可做语义细化。
- 录像小尺寸有锯齿和压缩，不能把一切纹理颗粒称为摩尔纹。A1/A2是几何/轮廓破碎，有独立纹理重建支持；高频采样闪烁应另用恒定视口、逐帧差分和不同采样设置复核。
- v9 真的在使用多姿态附件及分批切换；建议是修交接窗口和源图覆盖，不是“先引入附件切换”。
- 原版也会有可辨认的离散替换；目标不是数学意义上所有像素连续，而是接触、遮挡和动作重音可读。

### 直接证据链接

- [当前资产 JSON](https://github.com/backinfile/STS2_Konosuba_Megumin/blob/23d31cc4d17c0102f37aba65a650a29868e2556f/art/megumin-quartet-spine/actions-v9/export/megumin.json)
- [get_up 原生录像](https://github.com/backinfile/STS2_Konosuba_Megumin/blob/23d31cc4d17c0102f37aba65a650a29868e2556f/art/megumin-quartet-spine/actions-v9/verification/recordings/get_up.mp4)
- [relaxed_fall 原生录像](https://github.com/backinfile/STS2_Konosuba_Megumin/blob/23d31cc4d17c0102f37aba65a650a29868e2556f/art/megumin-quartet-spine/actions-v9/verification/recordings/relaxed_fall.mp4)
- [19动作录像目录](https://github.com/backinfile/STS2_Konosuba_Megumin/tree/23d31cc4d17c0102f37aba65a650a29868e2556f/art/megumin-quartet-spine/actions-v9/verification/recordings)

原版基线来自既有独立报告 此前交付的《杀戮尖塔2 Spine全量动画与大姿态切换分析》，其原版提交固定为 `64ed626b7ec9692bc54536b0123fc3cb580c28da`。这不是把当前惠惠与旧版惠惠混做比较。

### 结构交叉核验补充与优先级

- P1（先修）：A1/A2。这里P1指这份美术修复清单内的高优先级，不等于游戏崩溃级缺陷。
- P2（下一轮）：A3脚底/膝盖投影交接；再处理attack/cast及倒地/死亡的语义区分。
- P3（润色）：受击强度、吟唱持续张力、低幅呼吸与次级运动。

独立结构统计 [fold-metrics.json](data/fold-metrics.json) 对照各附件自身的 `_bind` 姿势：relaxed_fall 0.75s 的反向三角形面积主要在 cape（13.491，4个三角）；0.76667s cape约16.006（28个三角），与披风尖片像素相互支持。get_up 1.0s 的body反向三角形面积仅0.000708，不能据此把胸腹空洞归罪于翻面。其body在0.95s换kneel-rise、cape在1.05s、head/hands在1.08333s、两腿在1.11667/1.21667s交接，存在可验证的覆盖组合变化；但最终原因须逐slot隔离，可能涉及网格、附件覆盖与遮挡组合，不能称已证明的单一根因。

## 结构与时间轴量化


### 版本、范围和方法

- 仓库 main 只读检出：`23d31cc4d17c0102f37aba65a650a29868e2556f`。
- 实际默认构建资产：`art/megumin-quartet-spine/actions-v9/export/megumin.json`。依据 `tools/build-mod.ps1` 默认 Actions=actions-v9；运行时 `mod/MeguminVisuals.cs` 从 mod dist JSON/atlas 动态载入。不是 `art/.../export` 中的旧 v1。
- 独立使用官方 `@esotericsoftware/spine-core 4.2.120` 解析；对19正式动作按120Hz取样世界坐标；不执行仓库生成/验证脚本。JSON声明4.2.43。仓库自带 validation 只当旁证。
- 参考原版5个可玩角色的既有解码数据（原版源commit `64ed626b7ec9692bc54536b0123fc3cb580c28da`），不以复杂度或是否用IK直接判质量。
- 本分报告仅做结构与时间轴证据。运行时触发问题、网格换图和视觉破损另由集成/视觉报告核验。120Hz峰值是采样值，不声称连续域极值。

### 核心结论

没有发现JSON不可解析、负scale、权重未归一、设计端点不齐的硬性结构故障。最清楚的差距是动作语义重复、低幅同相待机、冗余烘焙和资源体积。局部肢体投影长度变化很大，是需看图验证的风险，不能直接认定为“骨长缩放bug”。

#### 中等：attack_short 与 cast_short 的视觉数据完全重复

- 两者都是1.496s。去掉events后，bones、slots、drawOrder各数据完全相同，并非仅姿态相似。
- 都在0.05、0.15、0.26667、0.4、0.5s逐步换到吟唱姿势，在1.01667至1.46667s沿相近路径回待机。
- 唯一区别是attack_short在0.76s有impact事件。cast_short没有事件。
- 因而攻击和施法本身没有不同的预备、发力、回收辨识度。若本来就要求共用吟唱动作，这属于可接受的设计取舍；若目标是原版那种技能语义清楚，应拆出攻击短促方向性和施法聚能姿态，而非单纯增加帧数。
- 原版5角色都有独立attack/cast，时长范围分别0.933–1.5s、0.967–1.875s。因此惠惠1.496s本身不是明显太长；重复的动作内容比时长更值得优先改。

#### 中低：循环有呼吸，但主要是上身同相微移，不能说“完全静止”

- idle_loop 3.4s：chest及其head、手臂、staff后代一起上下移动，峰峰1.4单位；cape额外左右约1.5单位。
- chant_loop 2.4s：上身峰峰0.8；披风左右约1.5。
- relaxed_loop 3.0s：上身峰峰约0.176；披风左右约1.5。
- 四个活动loop都只给chest/neck/cape_l/cape_r的translate非恒定值，所有rotate恒定。neck的反向补偿使它固定；head是chest直接子骨，随胸移动，不能混淆。
- 这意味着头部、手、法杖缺乏独立的角度/相位细节；脚在idle固定是优点，不是缺点。若视觉显得像贴纸，优先增加少量相位错开的头/手/杖/披风动作，而非增加网格密度。
- 原版idle keys 180–2769，结构更加分散；但“原版key多/骨多”不是质量定律。

#### 中低：明确的冗余关键帧，尚无实际卡顿证据

- 正式19动作合计215,200个runtime key，其中156,333个位于全程常量数值轨；共1,771条常量轨。
- 仅将这些常量数值轨保留一个初始key，就有154,562个重复key（占总key约71.8%）可作为无损压缩候选。仍须回归mixed playback和导出读取；这里未改资产。
- idle_loop共26,252 keys，25,420在恒定数值轨；原版Ironclad idle 180、Silent420、Necrobinder1037、Defect2505、Regent2769。
- 64骨每动作固定64 translate+64 rotate，全量60Hz烘焙；没有Scale/Deform/IK/Physics轨。缺少这些轨本身不构成问题，烘焙也能表现平滑；问题是大量常量重复让编辑和导出难维护。
- JSON 9,586,446 bytes，两个同内容扩展名的导出文件各一份；生产只需选择其中实际加载的一份。

#### 中低：图集资源较重，需实测后再定性能等级

- 18张图集页：12张2048×2048、6张2048×1024；PNG文件合计14,209,434 bytes。
- 按RGBA8888无压缩基础层计算240 MiB，若全部生成完整mip链约320 MiB。这个是资源预算估算，不是已经测到的Godot显存峰值。
- 每姿势多个大页留白，建议先检查紧凑重打包/合理分辨率，再做更多分片；透明区域和重复页的实际占用可继续优化。

### 需视觉复核的风险点（不能仅凭此判错）

世界坐标中相邻关节的二维距离变化：
- chant_enter，fore_r→hand_r：0.275s约4.312，0.61667s约41.505，约9.63倍。
- attack_short/cast_short：0.15s约4.700，1.2s约44.956，约9.57倍。
- get_up：3.45s约5.286，3.08333s约44.011。
- relaxed_fall中左前臂6.42–32.28，左右小腿约30.89–57.60、24.79–51.33。

所有骨local scale均为1，没有scale轨。上述变化来自translate和换角/关键姿势，不是scale动画失控。角色转侧面时前臂投影本来可以收短，应结合关节轮廓、握杖和附件切换前后截图判断压扁/橡皮感。主观“必须骨长永远固定”会误报。

### 已通过和应保留的项目

- 64骨、11槽、131个Mesh附件；全部加权。总30,458网格点/44,596三角形是所有姿势附件合计，并非单帧同时渲染量。
- 权重和范围0.9999899566–1.0000100434，属舍入量级。
- 17条设计端点转换独立逐顶点比较：最大距离0，附件一致、drawOrder一致。
- 5个loop首尾独立逐顶点比较：最大距离0，附件/层序一致。
- idle脚/脚尖世界坐标稳定，未发现站立待机滑脚。
- dead_from_down全0.45s、dead_loop全2s均全静态，作为死亡保持可合理；不是必然缺陷。
- 19正式动作+13 `_bind/` 校准姿势；bind不应当作正式战斗动作计入。
- 端点连续只证明设计接头；不证明任意时刻中断到另一动作平滑，也不证明附件切换中间没有像素跳变。游戏状态机能否正确选择这些转换需另查。

### 可复查材料

- [structural-metrics.json](data/structural-metrics.json)：19动作时长、轨道/key、二维关节长度极值、脚路径、事件、换附件时刻、图集和原版比较。
- [continuity-metrics.json](data/continuity-metrics.json)：17转换、5循环、loop世界骨运动范围、attack/cast精确等价。
- `structural.mjs`、`continuity.mjs`：独立只读官方runtime重放脚本。

源代码/资产永久链接：
https://github.com/backinfile/STS2_Konosuba_Megumin/blob/23d31cc4d17c0102f37aba65a650a29868e2556f/art/megumin-quartet-spine/actions-v9/export/megumin.json
https://github.com/backinfile/STS2_Konosuba_Megumin/blob/23d31cc4d17c0102f37aba65a650a29868e2556f/art/megumin-quartet-spine/actions-v9/export/megumin.atlas

### 与独立视觉复现交叉后的最高优先项

#### 高：get_up 约0.95–1.05s胸/肩/腰出现可见断裂/破洞样轮廓

视觉复现已在两条独立检查中确认，详见视觉图册。结构上可以定位到：body在0.95s先换kneel-rise；cape到1.05s、head/hands到1.08333s、leg_l/arm_l到1.11667s、arm_r到1.15s、leg_r到1.21667s才换。1.0s的身体是kneel-rise，而头、披风、四肢大部仍来自brace。

这是优先检查切片覆盖、遮挡、过渡权重和换图配合的时间窗；错峰换图不必然有错，也不能仅凭时间差就声称找到了唯一根因。独立三角翻面检查表明1.0s body翻面面积只有0.000708平方单位，整个可见网格合计约1.004，因此“胸洞就是大量三角翻面”缺乏支持。

#### 高：relaxed_fall 约0.72–0.7999s衣服/腰背出现细长黄刺，换图后消退

视觉复现支持这是可见瑕疵。独立三角方向检查（相对各附件对应_bind姿势）在0.75s发现合计15.740平方单位翻面，其中brace/cape为13.491（4三角）；0.76667s合计18.623，主要lower/cape为16.006（28三角）。body自身分别仅0.630、0.904。

因此可确定时间窗内存在网格折叠，尤其披风；但某个衣饰黄刺的具体来源还需槽隔离图验证，不能只按总翻面面积把所有可见问题归在body。0.8s换图后像素可能变好但别的不可见/小面积翻面仍在，几何风险值和视觉严重程度并不一一对应。

#### 审计方法上的关键差别

两项片段内部明显瑕疵，与17个设计接头和5个loop首尾完全通过并不冲突。验收不能只比较首尾骨坐标；应至少加入换附件前后一帧的渲染、各槽单独检查、三角翻面、最终画面像素/轮廓检查。新数据：[fold-metrics.json](data/fold-metrics.json)与独立`folds.mjs`。

## 运行时接入与验证边界


### 固定版本及结论

- 惠惠仓库：`23d31cc4d17c0102f37aba65a650a29868e2556f`。
- 原版源码参照：`Hexpion/Slay-the-spire-2@64ed626b7ec9692bc54536b0123fc3cb580c28da`；这是指定源码快照，不保证与所有游戏安装版本一致。
- 补充核对 BaseLib **v3.4.7** 对应提交 `c070755d11ec062f6c97c4dda1a205d975ed066a`，与项目 `docs/mod-lab.md:3` 声明版本一致。已通过 GitHub connector 读取该 tag 源码；没有运行 BaseLib DLL。
- 当前默认构建使用 **actions-v9**，不是历史 v6 Godot AnimationPlayer。`build-mod.ps1:1,17–21` 复制 v9 export JSON 为 `animation/megumin.spine-json`；`MeguminVisuals.cs:15–29` 动态加载 JSON/atlas 并创建 SpineSprite。
- 自行只读重算 v9 JSON SHA-256 为 `2691ef294c09da2ada158ad6e3c69454d5f83e3cf8aef7f171e710822946150b`，与提交的 delivery.json 相同；这不验证用户机器上的实际安装包。
- 生产代码映射的六个动画 ID 全部存在。19 个非 `_bind/` 动作均有各 slot 的 t=0 attachment key；没有发现“六个必要动画名拼错”或普遍“附件完全不复位”的问题。
- 本次是源码与提交证据审查，没有重新运行游戏、编辑器、构建或项目脚本；下列可复现场景是下一轮实机验证方案，不冒充已经实测。

### P1：普攻的伤害等待与动画发力点不匹配【源码确认的时序错配；画面幅度待实测】

`attack_short` 长 1.496 秒，`impact` 事件在 **0.76 秒**；但 Megumin 没覆写 `AttackAnimDelay`，继承 BaseLib 的 **0.15 秒**。原版 `AttackCommand.FromCard` 读取这个角色参数，执行时等待 `CreatureCmd.TriggerAnim` 后继续伤害，不等待 Spine 的 impact 事件。整个 mod 没有连接/消费 impact 或 release 的回调。

普通速度下名义差值为 **0.61 秒**，即伤害开始逻辑早于作者标注的发力点。游戏 speed、调度、后续 VFX 等会影响实机可见时刻，不能把 0.61 当作本次测得的逐帧延迟。连续打牌还有在 0.76 秒前重启 Attack 的风险，19 单项动作全部能播放也不能证明战斗观感正确。

复现：普通速度新开惠惠测试战斗，打初始牌 Strike，记录 `Attack` trigger、实际 HP 变化、Spine impact 的时间戳；再快速连出两张攻击牌，对比攻击是否重启、impact 是否到达。建议优先让普通攻击发力时刻与现有 0.15 秒节奏对齐，或明确调整角色等待；不要盲目把所有卡牌强制等待整段 1.496 秒。

证据：
- [Megumin 全类，没有延迟覆写](https://github.com/backinfile/STS2_Konosuba_Megumin/blob/23d31cc4d17c0102f37aba65a650a29868e2556f/mod/Megumin.cs#L14-L34)
- [BaseLib 3.4.7 默认延迟 0.15/0.25](https://github.com/Alchyr/BaseLib-StS2/blob/c070755d11ec062f6c97c4dda1a205d975ed066a/Abstracts/CustomCharacterModel.cs#L111-L114)
- [v9 调用共享生成器](https://github.com/backinfile/STS2_Konosuba_Megumin/blob/23d31cc4d17c0102f37aba65a650a29868e2556f/art/megumin-quartet-spine/tools/build_actions_v9.py#L28)
- [共享生成器 impact=0.76，cast 无事件](https://github.com/backinfile/STS2_Konosuba_Megumin/blob/23d31cc4d17c0102f37aba65a650a29868e2556f/art/megumin-quartet-spine/tools/build_actions_v7.py#L394-L400)
- [原版 AttackCommand 读取角色延迟](https://github.com/Hexpion/Slay-the-spire-2/blob/64ed626b7ec9692bc54536b0123fc3cb580c28da/Slay%20the%20Spire%202/src/Core/Commands/Builders/AttackCommand.cs#L142-L147)；[执行时等待动画参数](https://github.com/Hexpion/Slay-the-spire-2/blob/64ed626b7ec9692bc54536b0123fc3cb580c28da/Slay%20the%20Spire%202/src/Core/Commands/Builders/AttackCommand.cs#L383-L395)
- [TriggerAnim 等传入 waitTime，不等动画事件/整段时长](https://github.com/Hexpion/Slay-the-spire-2/blob/64ed626b7ec9692bc54536b0123fc3cb580c28da/Slay%20the%20Spire%202/src/Core/Commands/CreatureCmd.cs#L659-L690)

### P1：大姿态动画已制作，生产状态图仍是六状态【明确未接入，不等于素材缺失】

生产 `Megumin.SetupCustomAnimationStates` 调 BaseLib 通用 helper，实际为：idle_loop 循环；Attack→attack_short→idle_loop；Cast→cast_short→idle_loop；Hit→hit→idle_loop；Dead→dead 非循环停末帧；Relaxed→relaxed_loop 循环。没有吟唱、爆裂、relaxed_fall、get_up、hit_chant、hit_down、dead_from_down、dead_loop 或 Revive 分支。

由此可确定：
1. 若用通用 Relaxed 触发进入趴地，是直接切 relaxed_loop，跳过 1.4 秒 relaxed_fall；Idle 直接回站立，跳过 3.67 秒 get_up。
2. 若当前已趴地后触发 Hit，仍选站立版 hit 并回 standing idle；若触发 Dead，仍选从站姿开始的 dead，未选 dead_from_down。这些是现有状态图的条件性缺口。当前占位卡组是否会自然进入 Relaxed，尚未确认，不能说普通战斗必然已经遇到。
3. 玩家复活没有 Revive 分支时沿原版 fallback 淡出→ImmediatelySetIdle→淡入；不是播放 get_up。原版本身允许这种 fallback，所以它是高级起身接入未完成，不是通用框架错误。
4. dead 没后继 dead_loop **本身不构成 bug**：一次性死亡停末帧是原版默认，也有离线末端保持检查。需要尸体循环时再接。

项目已明确声明正式爆裂玩法尚未实现，不能把这个范围边界包装成对方承诺过的成品缺陷。但若目标是评估“19 动作是否已在游戏中形成完整行为”，答案是否定的。

复现：通过真正 CreatureAnimator 依次发送 Relaxed→Hit、Relaxed→Dead、Relaxed→Idle；不要用 `/animation` 直接播片替代。分别在 fall/get_up 中段发送 Hit/Dead（需先接入对应状态），记录当前逻辑状态和 track entry；再测玩家死亡后复活。

证据：
- [当前六状态入口](https://github.com/backinfile/STS2_Konosuba_Megumin/blob/23d31cc4d17c0102f37aba65a650a29868e2556f/mod/Megumin.cs#L30-L33)
- [BaseLib 通用状态与后继](https://github.com/Alchyr/BaseLib-StS2/blob/c070755d11ec062f6c97c4dda1a205d975ed066a/Abstracts/CustomCharacterModel.cs#L149-L194)
- [动作起点：dead 从 E00，dead_from_down 从 prone](https://github.com/backinfile/STS2_Konosuba_Megumin/blob/23d31cc4d17c0102f37aba65a650a29868e2556f/art/megumin-quartet-spine/tools/build_actions_v7.py#L379-L393)
- [原版复活与硬切 Idle fallback](https://github.com/Hexpion/Slay-the-spire-2/blob/64ed626b7ec9692bc54536b0123fc3cb580c28da/Slay%20the%20Spire%202/src/Core/Nodes/Combat/NCreature.cs#L592-L625)
- [项目公开声明玩法占位](https://github.com/backinfile/STS2_Konosuba_Megumin/blob/23d31cc4d17c0102f37aba65a650a29868e2556f/docs/mod-lab.md#L29-L33)

### P2：没有显式 mix 策略，无法保证任意时刻打断【配置缺口及未测风险】

MeguminVisuals 创建 SpineSkeletonDataResource 时只设 skeleton_file_res 和 atlas_res，没有 default_mix / animation_mixes 或 track mix override。不能未经插件实测就把未设置字段武断写成“mix=0”。可以确认的是：没有针对 idle→attack、hit→idle、攻击中段→hit、趴地→dead 等动作对配置接续。

原版 Ironclad 有显式 default_mix=0.05、idle→attack=0.1、idle→hurt=0.03、hurt→idle=0.1；它并非靠每个动画首末帧一致就解决所有切换。CreatureAnimator 触发动画时不显式 reset skeleton，任意时刻切出姿态和 mix 行为均需单独验证。大角度 attachment 离散换图遇到混合时还会有材质/轮廓跃变风险，不能由骨骼末帧误差证明无跳变。

复现：attack_short 在 0.15、0.45、0.75、1.1 秒分别被 Hit/Dead 打断，再测 Hit 重入、Attack→Attack 连发、Cast→Attack。抓实际 mix duration 和至少前后各数帧。倒地状态应先修正确路由，再调 mix；长 mix 不能补出缺失的起身动画。

证据：[Megumin 动态资源创建](https://github.com/backinfile/STS2_Konosuba_Megumin/blob/23d31cc4d17c0102f37aba65a650a29868e2556f/mod/MeguminVisuals.cs#L13-L29)；[原版 Ironclad mix](https://github.com/Hexpion/Slay-the-spire-2/blob/64ed626b7ec9692bc54536b0123fc3cb580c28da/Slay%20the%20Spire%202/animations/characters/ironclad/ironclad_skel_data.tres#L6-L37)；[原版 SetNextState/排队实现](https://github.com/Hexpion/Slay-the-spire-2/blob/64ed626b7ec9692bc54536b0123fc3cb580c28da/Slay%20the%20Spire%202/src/Core/Animation/CreatureAnimator.cs#L79-L121)。

### P2：现有“全通过”证明可播与指定接缝，不证明生产状态机正确【验证缺口】

现有证据有价值：记录了 19 动作、57 时刻、21 段原生视频、13 次出牌/回合操作胜利。项目也在 mod-lab.md 明说动作展示由测试接口触发，正常战斗由真实操作触发，不能说他们伪造了原生录像。

但覆盖边界非常明确：
- `/animation` 每次先 clear_tracks 再 set_animation；不经 CreatureAnimator、不走 NextState 队列，也不保留正常 mix-in/out 链。time 参数还把 time_scale 设为 0。
- full-sequence 由 Python 按 authoring duration sleep 后手动切下一个动作；它证明原生引擎能显示这组片段，不能证明生产状态机自动接续。
- 57 时刻测试只验证返回 PNG 和文件长度，不比较角色姿态或事件行为。
- 离线 frame 每次 new Skeleton，再单独 Animation.apply；17 接缝只比前一片段末帧与后一片段第 0 帧，未覆盖混合和中段打断。
- 事件检查将整段一次 apply，检查 impact/release 各出现一次；没有验证生产消费者、取消时不触发、重入时不重复、伤害时机匹配。
- 原生录像检查以 5fps 裁切测可见、是否变化、采集 fps；不是自然度、接缝、正确状态或战斗时序断言。
- 真正 CreatureAnimator 的 idle 有初始随机相位和循环 0.9–1.1 倍速；手动录片默认原速从头播放，不覆盖这些参数差异。

建议增加三层回归：真实 trigger/状态/track 日志；带游戏 HP/VFX 时刻的时序断言；任意时刻打断与恢复组合录像。不要增加更多同一片段首中尾截图来代替这些缺口。

证据：
- [测试接口 clear_tracks / set_animation / 冻结](https://github.com/backinfile/STS2_Konosuba_Megumin/blob/23d31cc4d17c0102f37aba65a650a29868e2556f/mod/LabApi.cs#L88-L104)
- [Python 手动 sleep 拼接](https://github.com/backinfile/STS2_Konosuba_Megumin/blob/23d31cc4d17c0102f37aba65a650a29868e2556f/tools/record-native-animations.py#L20-L57)
- [57 时刻测试](https://github.com/backinfile/STS2_Konosuba_Megumin/blob/23d31cc4d17c0102f37aba65a650a29868e2556f/tools/test-lab.py#L37-L47)
- [独立新 skeleton 采样](https://github.com/backinfile/STS2_Konosuba_Megumin/blob/23d31cc4d17c0102f37aba65a650a29868e2556f/art/megumin-quartet-spine/tools/v7_runtime.mjs#L12)
- [首末帧接缝及一次性事件检查](https://github.com/backinfile/STS2_Konosuba_Megumin/blob/23d31cc4d17c0102f37aba65a650a29868e2556f/art/megumin-quartet-spine/tools/validate_actions_v7.mjs#L31-L38)
- [视频检查阈值](https://github.com/backinfile/STS2_Konosuba_Megumin/blob/23d31cc4d17c0102f37aba65a650a29868e2556f/tools/verify-native-recordings.py#L8-L23)
- [原版随机 idle 初相](https://github.com/Hexpion/Slay-the-spire-2/blob/64ed626b7ec9692bc54536b0123fc3cb580c28da/Slay%20the%20Spire%202/src/Core/Animation/CreatureAnimator.cs#L33-L53)；[循环速度/相位偏移](https://github.com/Hexpion/Slay-the-spire-2/blob/64ed626b7ec9692bc54536b0123fc3cb580c28da/Slay%20the%20Spire%202/src/Core/Animation/CreatureAnimator.cs#L159-L163)

### 小问题与不能误报项

- README 第 61 行仍称 actions-v8 为“当前 Spine 动画”，但首页入口、构建默认、mod-lab 均指 v9；是导航残留，不是运行时仍用 v8。
- 静态 Bounds/CenterPos 等没有随趴地切换（MeguminVisuals.cs:31–35），可列为日后大姿态接入的交互框验证项；尚未测裁切/命中框，不能宣称已经不可点击。
- 没有 physics/IK/某类约束、使用分角度 attachment 或单 track，单独都不等于 bug。原版也有不同结构，必须回到角色风格和实际画面。
- 六通用动画都存在、loop 参数正确区分 idle/relaxed 与一次性 attack/cast/hit/dead。不要因 `_loop` 命名或 dead_loop 未接入而误报“死亡自动复活”。
