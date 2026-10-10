# Spine 动画连续性检查脚本

这套 Node.js CLI 能找出“帧与帧之间哪里值得检查”，支持 Spine 4.2 JSON / binary `.skel`。它使用官方 `@esotericsoftware/spine-core@4.2.120` 求解骨骼、约束、deform 和 AnimationState 混合，不是简单数关键帧。

**输出连续性风险信号，不输出未经验证的 0–100 丝滑分。** 流畅度还有审美、意图、纹理覆盖、轮廓、摄影机和真实播放掉帧等因素，几何指标不能完整代替目测。

## 安装与快速开始

需要 Node.js 20 或更新版本。从仓库根进入 `tools/spine-smoothness-auditor`，或将工具单独复制后在其目录执行：

```bash
npm ci --ignore-scripts
npm test
node bin/spine-audit.mjs --help
node bin/spine-audit.mjs --input fixtures/synthetic.json --loops smooth_loop,closed_velocity_kink --out out-demo
```

运行只在本地读文件并写结果，不上传素材，不修改输入，不需要 Spine 编辑器可执行文件，也不加载项目里的自定义脚本。安装依赖需要访问 npm 官方仓库；装好后检查可离线运行。依赖的使用、集成和分发须遵守包内 `SPINE-RUNTIMES-LICENSE.txt`，并自行确认所需 Spine Editor 授权；本脚本不授予 Spine 或素材授权。

## 常用命令

先看动画名称：

```bash
node bin/spine-audit.mjs --input /path/hero.json --list
node bin/spine-audit.mjs --input /path/hero.skel --list
```

检查动画内部以及 idle 的循环接缝：

```bash
node bin/spine-audit.mjs --input /path/hero.json --atlas /path/hero.atlas --animations idle_loop,attack,get_up --loops idle_loop --fps 60 --out out/hero
```

`.atlas` 只读元数据，不需要 PNG。默认自动寻找与输入同名的 `.atlas`；没有 atlas 时照常检查骨骼和 mesh，但跳过 region 四角，避免将裁边/旋转信息缺失造成的假坐标当成结果。

模拟某个时刻真正开始的 mix：

```bash
node bin/spine-audit.mjs --input /path/hero.json --animations attack,idle_loop --transition attack:idle_loop --from-time 0.45 --mix 0.2 --to-loop --fps 120 --out out/mix
```

`--from-time` 是源动画开始切换的相位，不是取两动画端点做线性插值。源动画从 0 顺序跑到该时刻，再调用 `AnimationState.setAnimation`，设置目标 entry 的 mix duration；mix 中两条动画都继续前进。默认单轨、目标从 0 开始、两个动画均不循环。源需要循环时加 `--from-loop`。所有过渡报告以切换时刻为 0，负数表示切换前。未指定 fromTime 时用源动画结束时刻。硬切换使用 `--mix 0`。

切换前后同一时刻的位置跳变写入 `switchInstant`，不为同一时刻虚构时间差。过渡中的逐帧速度仍按采样间隔计算。游戏里的多轨叠加、事件驱动中断、timeScale、holdPrevious、additive 和自定义 mixing 需要另行复现。

排除辅助骨骼或只检查特定部位：

```bash
node bin/spine-audit.mjs --input /path/hero.skel --bones "head|body|arm" --ignore-bones "helper|backup" --slots "body|cape" --mesh-vertices 64 --out out/body
node bin/spine-audit.mjs --input /path/hero.skel --visible-bones-only --out out/visible-dependencies
```

参数为 JavaScript 正则表达式，区分大小写。`--bones` 不限制 slot 顶点；`--slots` 不限制骨点。`--visible-bones-only` 只保留当时可见附件的父链/加权骨依赖；不反向追溯 IK/transform constraint 目标，不等于屏幕像素可见。

启用 Spine physics constraints：

```bash
node bin/spine-audit.mjs --input /path/hero.skel --physics update --fps 120 --out out/physics
```

默认 `none`，报告明确列出被禁用的 physics constraint 数量。`update` 按顺序调用 state.update/apply、skeleton.update、updateWorldTransform(Physics.update)，不会逐帧重置物理。从 reset 起跑，没有自动预热到稳态；最初的物理瞬态保留在结果中。动画网格使用 `dt=duration/ceil(duration*fps)` 的固定步长，所以精确采到终点且实际 FPS 略大于或等于请求值。过渡 warm-up 同样精确抵达 fromTime，之后使用 `1/fps`。未模拟引擎对 skeleton 的外部平移/转动以及 physicsTranslate/physicsRotate。

## 输出文件与怎么读

- `report.md`：可读汇总、最强信号、具体时间、骨骼/slot、循环和 mix 结果、限制
- `report.json`：完整统计、每个点的 speed/acceleration/jerk、全部事件、配置、输入 SHA-256 和运行时版本
- `frames.csv`：每个采样帧对应支持区间的最大导数及最强点；不是实时引擎 FPS
- `signals.csv`：连续性信号、附件/可见性/层序事件、网格三角形提示及其时间

CSV 用 UTF-8，建议通过电子表格的“导入 UTF-8 CSV”打开。JSON 的 `byKind.bone` 与 `byKind["visible-geometry"]` 独立，避免辅助骨瞬移淹没画面顶点的表现。`signalCount` 是 **点 × 时间 × 指标** 的诊断记录数量，不是缺陷个数；不要据此给不同角色排名。

优先读：

1. `loopSeam` 的位置、速度与附件事件。位置相等不代表速度方向相等；不足 5 个匹配样本时速度接缝未知。
2. `switchInstant` 和切换前后的 `perFrame`，确认真实 mix 的中段，而不只比较两个端点。
3. `continuitySignals` 中最强的 visible-geometry 和关键骨。`supportStart/supportEnd` 给出导数真正用到的原始帧区间，不把 jerk 峰值误当成唯一坏帧。
4. `discreteEvents`，尤其是同一 slot 换附件、隐藏、alpha 大步变化、序列帧和 draw order 改变。
5. `geometryEvents`，检查 mesh 三角形近退化或翻面；这些是独立提示，故意透视压扁和镜像也可能出现。

## 指标定义

先固定参考长度 S，再对世界坐标除以 S。默认 S 是 setup pose 可见 region/mesh 顶点包围盒的对角线；缺乏有效可见几何时依次退回 skeleton 导出 bounds、setup 骨骼范围、1。**它不是 Spine physics 的 referenceScale 参数。** 可用 `--scale` 提供明确角色身高等标尺；报告记录实际来源。换 skin 后会重新计算，跨角色比较最好统一标尺定义。

- 骨骼取 origin、x 轴端点、y 轴探针，包含父子变换/IK/transform/path constraints。零长度骨仍有尺度为 0.03S 的方向探针。
- region 取四角；mesh 默认均匀抽取最多 16 个顶点，deform 与权重通过 runtime 求解。可调高 `--mesh-vertices` 直到覆盖全部顶点。
- step：相邻归一化点的位移；单位 S。
- speed：相邻点向量差 / 实际秒数；单位 S/s。
- acceleration、jerk：对速度、加速度向量继续按真实时间间隔求差分；单位 S/s²、S/s³。先向量差后取模，恒速转弯仍有向心加速度。
- loop position：t=0 与 t=duration 的同身份点距离。
- loop velocity：两端 5 点四阶单侧导数之差；以 3 点与 5 点估计的差作为截断误差提示。只有 gap > 阈值 + 误差提示才标风险。它不是严格误差上界，仍需更高 FPS 验证；已防止匀速圆周运动被低阶差分误报为接缝。

不把角度 179°→−179° 的数值差直接当 358° 跳变，而是看 runtime 求解后的世界点轨迹。真实多圈旋转只要采样足够会保留运动。快速旋转可能发生采样混叠，甚至看似静止；`angularAliasingRisks` 会根据 RotateTimeline 的键间平均速率提示 ≥90°/采样的片段，但 Bézier 峰值/父链叠加更快，不保证全部识别。

风险门槛按每个点、每个指标计算：

`max(absoluteFloor, median + madMultiplier × max(1.4826 × MAD, 0.05 × median, 1e-9))`

默认 floor：step 0.03、speed 3、acceleration 60、jerk 3000；MAD 倍数 8。loop position 0.002、loop velocity 0.1。**这些是可调整的筛查默认值，没有声称是审美/行业合格线。** 恒定高速通常不会作为尖峰触发，但绝对速度保留在 summary/landmarks。完全静止同样可能“无尖峰”，不代表动作自然。

每帧并行比较相同 attachment identity 的顶点；换附件、暂时隐藏、不同拓扑不会被错误配对求导，因此材质轮廓的跳变需要读离散事件并目测。即使骨轨、全部三角形方向都正常，纹理覆盖不足仍可能出现背景洞。

三角形检查使用全部顶点/全部三角形，独立于采样上限。signed area 变号记录翻面，面积相对首次可见姿势跌至默认 2% 或数值近零记录退化；重复保持退化不会每帧报同一事件。首次姿势可能已有变形，这不是健康 rest pose 检验。

## 标注意图明确的顿帧、打击、保持

不要为了把所有数值压低而抹平动作设计。`config.example.json` 展示阈值、过滤、mix 和 suppression 配置：

```bash
node bin/spine-audit.mjs --input /path/hero.json --config config.example.json --out out/reviewed
```

`suppressions` 可按动画/过渡名称、时间区间、bone/slot 正则、指标指定原因。与导数支持区间相交的信号会保留记录，但设为 suppressed，不计入待检查信号数。

`--suppress-stepped` 只自动标注直接对应 bone/slot 的 stepped key 区间，不自动影响子骨、约束目标或其他附件；复杂冲击动作建议使用显式区间。默认不会自动忽略 stepped，以免把错误阶跃隐藏。

## 已验证与示例

`npm test` 使用 Node 内置测试器，测试合成恒速/静止、真实跳变、world-angle wrap、多圈旋转、闭位置但速度不闭合、附件切换/隐藏、weighted mesh、deform、零时长、真实 runtime mix、物理、尺度不变性和异常输入。`qa/README.md` / QA 结果提供独立回归说明。

[`examples/`](examples/README.md) 含合成报告、Megumin v9 和原版骨骼的派生可读报告与精简摘要；完整 JSON / CSV 按说明重跑生成，未随仓库提交。**不包含游戏原始 JSON、skel、atlas、图片、视频或 node_modules。** 示例用于解释输出，不是已校准的“角色质量排行榜”。输入 SHA-256 在报告内，完整的实际回归范围见 `VALIDATION.md`。

## 限制

- 只支持 Spine 4.2。4.1、3.8、4.3 等拒绝解析，不能靠盲改版本字符串兼容。
- 不读取纹理和像素；不判断透明像素、纹理缝、覆盖背景洞、轮廓一致性、穿插遮挡、clipping、模糊或抗锯齿。
- 不测真实引擎的帧时间、卡顿、掉帧、GC、GPU 性能；需另加运行时 frame-time profiler。
- 纯运动学也不能判断表现意图。匀速机械动作、一直静止可能几何平滑但表演生硬。
- finite difference 对采样率、真实不连续、精度噪声敏感；相同 FPS/参考长度/skin/可见性/顶点数/物理设置才可比较。建议重要信号用 60/120/240 FPS 验证并在播放器逐帧核验。
- 统计对所有采样点汇总，骨骼/网格密度和抽样方式影响 p95/p99；不要简单跨 rig 排名。
- 默认单个分析最多 20,000 帧；JSON config 可调 `maxFrames`。网格点数和采样帧数很大时内存/时间会上升。

官方参考：
- [Spine runtime skeletons / world transforms](https://esotericsoftware.com/spine-runtime-skeletons)
- [AnimationState / applying animations](https://esotericsoftware.com/spine-applying-animations)
- [Spine runtimes](https://github.com/EsotericSoftware/spine-runtimes)
- [Spine runtimes license](https://esotericsoftware.com/spine-runtimes-license)
