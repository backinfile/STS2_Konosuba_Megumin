# Spine 连续性风险检查

输入：silent.skel · Spine 4.2.43 · runtime 4.2.120
参考长度：1280.67536 (setup-visible geometry bounding-box diagonal (before clipping/occlusion))
采样：请求 60 FPS；物理：none；可见网格每附件最多 16 个顶点。

速度、加速度和 jerk 均已按固定参考长度归一化。风险计数是“点×时间×指标”的诊断数量，不是缺陷数量，也不能当分数排名。

## 汇总

| 动画/过渡 | 时长 s | 风险信号 | 已标注意图 | 附件/层序等事件 | 网格提示 | loop位置差 | loop速度差 |
|---|---:|---:|---:|---:|---:|---:|---:|
| idle_loop | 1.067 | 33 | 0 | 0 | 0 | 0.00000 | 2.63345 |
| attack | 0.933 | 11982 | 0 | 37 | 39 | n/a | n/a |
| attack -> idle_loop | 0.498 | 1289 | 0 | 1 | 0 | n/a | n/a |

## idle_loop

实际采样 66 帧，有效 FPS 60.937。
仅在准备循环播放时解读：端点位置风险 false，端点速度风险 false；附件/层序接缝事件 0。速度采用5点高阶单侧差分，对比3点结果估计误差：11.05340；误差估计不是严格界限，需提高FPS复验。

最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：
- 1.0421 s [1.0174, 1.0667]：jerk=47898.43075，阈值=3000.00000；bone:blade_shine/origin（未识别为可见附件依赖骨）
- 1.0421 s [1.0174, 1.0667]：jerk=46669.71120，阈值=3000.00000；bone:blade_shine/x-axis（未识别为可见附件依赖骨）
- 1.0256 s [1.0010, 1.0503]：jerk=46353.42436，阈值=3000.00000；bone:blade_shine/origin（未识别为可见附件依赖骨）
- 1.0421 s [1.0174, 1.0667]：jerk=46140.36509，阈值=3000.00000；bone:blade_shine/y-axis（未识别为可见附件依赖骨）
- 1.0256 s [1.0010, 1.0503]：jerk=46103.66586，阈值=3000.00000；bone:blade_shine/y-axis（未识别为可见附件依赖骨）
- 1.0256 s [1.0010, 1.0503]：jerk=45682.61586，阈值=3000.00000；bone:blade_shine/x-axis（未识别为可见附件依赖骨）
- 1.0338 s [1.0174, 1.0503]：acceleration=786.81449，阈值=60.00000；bone:blade_shine/y-axis（未识别为可见附件依赖骨）
- 1.0338 s [1.0174, 1.0503]：acceleration=786.02557，阈值=60.00000；bone:blade_shine/origin（未识别为可见附件依赖骨）
- 1.0338 s [1.0174, 1.0503]：acceleration=778.55637，阈值=60.00000；bone:blade_shine/x-axis（未识别为可见附件依赖骨）
- 1.0585 s [1.0503, 1.0667]：step=0.21579，阈值=0.03000；bone:blade_shine/y-axis（未识别为可见附件依赖骨）
- 1.0421 s [1.0338, 1.0503]：step=0.20764，阈值=0.03000；bone:blade_shine/y-axis（未识别为可见附件依赖骨）
- 1.0585 s [1.0503, 1.0667]：step=0.20623，阈值=0.03000；bone:blade_shine/x-axis（未识别为可见附件依赖骨）

## attack

实际采样 58 帧，有效 FPS 61.071。

最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：
- 0.0246 s [0.0000, 0.0491]：jerk=422650.45645，阈值=3000.00000；bone:attack_cape_anchor_arm_f/x-axis（未识别为可见附件依赖骨）
- 0.0246 s [0.0000, 0.0491]：jerk=421567.53848，阈值=3000.00000；bone:attack_cape_attach_arm_f/origin（未识别为可见附件依赖骨）
- 0.0246 s [0.0000, 0.0491]：jerk=421567.53848，阈值=3000.00000；bone:attack_cape_attach_arm_f/x-axis（未识别为可见附件依赖骨）
- 0.0246 s [0.0000, 0.0491]：jerk=421567.53848，阈值=3000.00000；bone:attack_cape_attach_arm_f/y-axis（未识别为可见附件依赖骨）
- 0.0246 s [0.0000, 0.0491]：jerk=421434.38852，阈值=3000.00000；bone:attack_cape_anchor_arm_f/origin（未识别为可见附件依赖骨）
- 0.0246 s [0.0000, 0.0491]：jerk=420386.37232，阈值=3000.00000；bone:attack_cape_anchor_arm_f/y-axis（未识别为可见附件依赖骨）
- 0.0737 s [0.0491, 0.0982]：jerk=359693.45447，阈值=3000.00000；bone:attack_cape_attach_should_b/y-axis（未识别为可见附件依赖骨）
- 0.0737 s [0.0491, 0.0982]：jerk=359693.45413，阈值=3000.00000；bone:attack_cape_should_b/y-axis（未识别为可见附件依赖骨）
- 0.0737 s [0.0491, 0.0982]：jerk=359677.44447，阈值=3000.00000；bone:attack_cape_attach_should_b/origin（未识别为可见附件依赖骨）
- 0.0737 s [0.0491, 0.0982]：jerk=359677.44413，阈值=3000.00000；bone:attack_cape_should_b/origin（未识别为可见附件依赖骨）
- 0.0737 s [0.0491, 0.0982]：jerk=359671.25205，阈值=3000.00000；bone:attack_cape_attach_should_b/x-axis（未识别为可见附件依赖骨）
- 0.0737 s [0.0491, 0.0982]：jerk=359671.25172，阈值=3000.00000；bone:attack_cape_should_b/x-axis（未识别为可见附件依赖骨）

离散事件（独立报告，不自动扣分）：
- 0.0164 s：attachment-change top arm cloak top arm cloak →
- 0.0164 s：visibility-change top arm cloak true → false
- 0.0327 s：attachment-change cape_front_attack  → cape_front_attack
- 0.0327 s：visibility-change cape_front_attack false → true
- 0.0491 s：attachment-change cloak back cloak back →
- 0.0491 s：visibility-change cloak back true → false
- 0.0491 s：attachment-change back arm cloak back back arm cloak back →
- 0.0491 s：visibility-change back arm cloak back true → false
- 0.0491 s：attachment-change right cape right cape →
- 0.0491 s：visibility-change right cape true → false
- 0.0819 s：attachment-change clipper  → clipper
- 0.0819 s：visibility-change clipper false → true

网格风险提示（先确认是否为有意透视/镜像）：
- 0.0164 s：triangle-orientation-flip，cloak back/cloak back，三角面 7 个
- 0.0164 s：triangle-orientation-flip，dress/dress，三角面 1 个
- 0.0164 s：triangle-orientation-flip，badge/badge，三角面 3 个
- 0.0327 s：triangle-orientation-flip，cloak back/cloak back，三角面 1 个
- 0.0327 s：triangle-orientation-flip，back arm cloak/back arm cloak，三角面 1 个
- 0.0327 s：triangle-orientation-flip，torso copy/torso copy，三角面 1 个
- 0.0327 s：triangle-orientation-flip，badge/badge，三角面 2 个
- 0.0491 s：triangle-orientation-flip，back arm cloak/back arm cloak，三角面 1 个
- 0.0655 s：triangle-collapse，back arm cloak/back arm cloak，三角面 1 个
- 0.0655 s：triangle-orientation-flip，back arm cloak/back arm cloak，三角面 1 个
- 0.0655 s：triangle-orientation-flip，dress/dress，三角面 1 个
- 0.0982 s：triangle-collapse，dress/dress，三角面 2 个

角度欠采样警告：
- hand_l，0.0642–0.0667 s：平均每采样步约 1130.0 度，当前结果可能把快速转动误读成静止。

## attack -> idle_loop

实际采样 31 帧，有效 FPS 60.000。切换时间记作 0；从动画相位 0.933 s，mix=0.200 s。
切换瞬间最大同身份点位置差：0.00000；附件/层序事件 1。

最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：
- -0.0737 s [-0.0982, -0.0491]：jerk=45910.42772，阈值=3000.00000；bone:attack_cape_anchor_leg_flap1/x-axis（未识别为可见附件依赖骨）
- -0.0737 s [-0.0982, -0.0491]：jerk=40951.43065，阈值=3000.00000；bone:attack_cape_anchor_leg_flap1/origin（未识别为可见附件依赖骨）
- -0.0737 s [-0.0982, -0.0491]：jerk=40556.07084，阈值=3000.00000；bone:attack_cape_anchor_leg_flap1/y-axis（未识别为可见附件依赖骨）
- -0.0573 s [-0.0819, -0.0327]：jerk=22512.88316，阈值=3000.00000；bone:attack_cape_anchor_leg_flap1/x-axis（未识别为可见附件依赖骨）
- -0.0573 s [-0.0819, -0.0327]：jerk=20094.35406，阈值=3000.00000；bone:attack_cape_anchor_leg_flap1/origin（未识别为可见附件依赖骨）
- -0.0573 s [-0.0819, -0.0327]：jerk=19989.95836，阈值=3000.00000；bone:attack_cape_anchor_leg_flap1/y-axis（未识别为可见附件依赖骨）
- -0.0082 s [-0.0327, 0.0167]：jerk=19648.03435，阈值=3000.00000；bone:attack_cape_anchor_arm_f/y-axis（未识别为可见附件依赖骨）
- -0.0082 s [-0.0327, 0.0167]：jerk=19648.03435，阈值=3000.00000；bone:attack_cape_attach_arm_f/origin（未识别为可见附件依赖骨）
- -0.0082 s [-0.0327, 0.0167]：jerk=19648.03435，阈值=3000.00000；bone:attack_cape_anchor_arm_flap1/y-axis（未识别为可见附件依赖骨）
- -0.0082 s [-0.0327, 0.0167]：jerk=19648.03435，阈值=3000.00000；bone:attack_cape_anchor_arm_flap1/origin（未识别为可见附件依赖骨）
- -0.0082 s [-0.0327, 0.0167]：jerk=19648.03435，阈值=3000.00000；bone:attack_cape_anchor_arm_flap1/x-axis（未识别为可见附件依赖骨）
- -0.0082 s [-0.0327, 0.0167]：jerk=19648.03435，阈值=3000.00000；bone:attack_cape_anchor_arm_f/origin（未识别为可见附件依赖骨）

离散事件（独立报告，不自动扣分）：
- 0.0000 s：attachment-change slash slash →

## 可信范围与限制

- Continuity risk signals are review candidates, not an aesthetic score or universal quality standard. Deliberate impacts/holds can produce strong signals.
- Geometry only: no pixels/textures, silhouette matching across attachment swaps, perceptual salience, occlusion, clipping, anti-aliasing, camera motion or real frame pacing.
- Single skeleton, skin and track 0 only. Match production tracks, timeScale, mix configuration, interruptions and engine behavior separately.
- Finite sampling can miss subframe jumps or alias fast rotations (especially >=180 degrees/sample). Verify suspect times at 2x/4x FPS.
- Derivative magnitudes depend on FPS around actual discontinuities; compare identical settings. Quantiles pool landmarks, so rig density can bias cross-character comparisons.
- Bone probes include helper bones by default; use visible-geometry summaries, --visible-bones-only or bone filters. Bone influence is a dependency approximation, not pixel visibility.
- Triangle collapse/flip is a geometric hint, not proof of a rendering defect. First visible pose is the reference and may already be distorted.

## 下一步

1. 先看 visible-geometry 与具体 slot/bone；再看被标记区间和附件事件。
2. 用相同设置在 60/120/240 FPS 复验；真实阶跃的导数通常随 FPS 增长，有限差分噪声也会变大。
3. 在原播放器逐帧检查命中/急停/换姿势是否有意；用 config.suppressions 标注意图，保留审计记录。
4. loop 要同时检查位置与速度；实际切换必须用运行时 mix 配置模拟，端点相等并不能保证中段无褶皱或像素跳。
