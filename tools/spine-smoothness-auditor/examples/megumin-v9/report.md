# Spine 连续性风险检查

输入：megumin.json · Spine 4.2.43 · runtime 4.2.120
参考长度：417.69568 (setup-visible geometry bounding-box diagonal (before clipping/occlusion))
采样：请求 60 FPS；物理：none；可见网格每附件最多 16 个顶点。

速度、加速度和 jerk 均已按固定参考长度归一化。风险计数是“点×时间×指标”的诊断数量，不是缺陷数量，也不能当分数排名。

## 汇总

| 动画/过渡 | 时长 s | 风险信号 | 已标注意图 | 附件/层序等事件 | 网格提示 | loop位置差 | loop速度差 |
|---|---:|---:|---:|---:|---:|---:|---:|
| idle_loop | 3.400 | 0 | 0 | 0 | 5 | 0.00000 | 0.00001 |
| chant_loop | 2.400 | 0 | 0 | 0 | 1 | 0.00000 | 0.00001 |
| get_up | 3.670 | 17 | 0 | 97 | 162 | n/a | n/a |
| relaxed_fall | 1.400 | 0 | 0 | 36 | 91 | n/a | n/a |
| hit | 0.420 | 0 | 0 | 0 | 9 | n/a | n/a |
| explosion_release | 0.700 | 0 | 0 | 9 | 3 | n/a | n/a |
| chant_enter -> chant_loop | 0.500 | 0 | 0 | 0 | 1 | n/a | n/a |

## idle_loop

实际采样 206 帧，有效 FPS 60.294。
仅在准备循环播放时解读：端点位置风险 false，端点速度风险 false；附件/层序接缝事件 0。速度采用5点高阶单侧差分，对比3点结果估计误差：0.00001；误差估计不是严格界限，需提高FPS复验。

最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：
- 当前阈值下无信号；不等于视觉完美。

网格风险提示（先确认是否为有意透视/镜像）：
- 0.0000 s：triangle-collapse，cape/E00/cape，三角面 2 个
- 2.1561 s：triangle-collapse，cape/E00/cape，三角面 1 个
- 2.1727 s：triangle-orientation-flip，cape/E00/cape，三角面 1 个
- 2.9356 s：triangle-collapse，cape/E00/cape，三角面 1 个
- 2.9522 s：triangle-orientation-flip，cape/E00/cape，三角面 1 个

## chant_loop

实际采样 146 帧，有效 FPS 60.417。
仅在准备循环播放时解读：端点位置风险 false，端点速度风险 false；附件/层序接缝事件 0。速度采用5点高阶单侧差分，对比3点结果估计误差：0.00002；误差估计不是严格界限，需提高FPS复验。

最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：
- 当前阈值下无信号；不等于视觉完美。

网格风险提示（先确认是否为有意透视/镜像）：
- 0.0000 s：triangle-collapse，cape/E12/cape，三角面 2 个

## get_up

实际采样 222 帧，有效 FPS 60.218。

最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：
- 3.2465 s [3.2382, 3.2548]：step=0.04263，阈值=0.03514；slot:staff/rigid_staff#default/rigid_staff/v0
- 3.2631 s [3.2548, 3.2714]：step=0.04226，阈值=0.03514；slot:staff/rigid_staff#default/rigid_staff/v0
- 3.2299 s [3.2216, 3.2382]：step=0.04220，阈值=0.03514；slot:staff/rigid_staff#default/rigid_staff/v0
- 3.2465 s [3.2382, 3.2548]：step=0.04307，阈值=0.03594；slot:staff/rigid_staff#default/rigid_staff/v2
- 3.2631 s [3.2548, 3.2714]：step=0.04273，阈值=0.03594；slot:staff/rigid_staff#default/rigid_staff/v2
- 3.2299 s [3.2216, 3.2382]：step=0.04253，阈值=0.03594；slot:staff/rigid_staff#default/rigid_staff/v2
- 3.2798 s [3.2714, 3.2881]：step=0.04105，阈值=0.03514；slot:staff/rigid_staff#default/rigid_staff/v0
- 3.2133 s [3.2050, 3.2216]：step=0.04091，阈值=0.03514；slot:staff/rigid_staff#default/rigid_staff/v0
- 3.2798 s [3.2714, 3.2881]：step=0.04146，阈值=0.03594；slot:staff/rigid_staff#default/rigid_staff/v2
- 3.2133 s [3.2050, 3.2216]：step=0.04108，阈值=0.03594；slot:staff/rigid_staff#default/rigid_staff/v2
- 3.2964 s [3.2881, 3.3047]：step=0.03898，阈值=0.03514；slot:staff/rigid_staff#default/rigid_staff/v0
- 3.1967 s [3.1884, 3.2050]：step=0.03882，阈值=0.03514；slot:staff/rigid_staff#default/rigid_staff/v0

离散事件（独立报告，不自动扣分）：
- 0.2325 s：attachment-change body prone/body → lower/body
- 0.2325 s：attachment-change leg_l prone/leg_l → lower/leg_l
- 0.2325 s：attachment-change leg_r prone/leg_r → lower/leg_r
- 0.2325 s：attachment-change arm_l prone/arm_l → lower/arm_l
- 0.2325 s：attachment-change hand_l prone/hand_l → lower/hand_l
- 0.2325 s：attachment-change arm_r prone/arm_r → lower/arm_r
- 0.2325 s：attachment-change head prone/head → lower/head
- 0.2325 s：attachment-change hand_r prone/hand_r → lower/hand_r
- 0.2823 s：attachment-change cape prone/cape → lower/cape
- 0.5148 s：attachment-change leg_r lower/leg_r → brace/leg_r
- 0.5812 s：attachment-change body lower/body → brace/body
- 0.5812 s：attachment-change leg_l lower/leg_l → brace/leg_l

网格风险提示（先确认是否为有意透视/镜像）：
- 0.0332 s：triangle-orientation-flip，cape/prone/cape，三角面 1 个
- 0.1993 s：triangle-orientation-flip，arm_l/prone/arm_l，三角面 1 个
- 0.2159 s：triangle-collapse，arm_l/prone/arm_l，三角面 3 个
- 0.2159 s：triangle-orientation-flip，arm_l/prone/arm_l，三角面 3 个
- 0.2491 s：triangle-orientation-flip，body/lower/body，三角面 1 个
- 0.2989 s：triangle-orientation-flip，cape/lower/cape，三角面 1 个
- 0.3155 s：triangle-orientation-flip，cape/lower/cape，三角面 1 个
- 0.3321 s：triangle-collapse，body/lower/body，三角面 1 个
- 0.3321 s：triangle-orientation-flip，body/lower/body，三角面 1 个
- 0.3653 s：triangle-orientation-flip，body/lower/body，三角面 1 个
- 0.3653 s：triangle-collapse，leg_r/lower/leg_r，三角面 1 个
- 0.3653 s：triangle-orientation-flip，leg_r/lower/leg_r，三角面 1 个

## relaxed_fall

实际采样 85 帧，有效 FPS 60.000。

最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：
- 当前阈值下无信号；不等于视觉完美。

离散事件（独立报告，不自动扣分）：
- 0.1333 s：attachment-change leg_r fall-lean/leg_r → crouch/leg_r
- 0.1833 s：attachment-change cape fall-lean/cape → crouch/cape
- 0.1833 s：attachment-change leg_l fall-lean/leg_l → crouch/leg_l
- 0.1833 s：attachment-change hand_l fall-lean/hand_l → crouch/hand_l
- 0.1833 s：attachment-change head fall-lean/head → crouch/head
- 0.1833 s：attachment-change hand_r fall-lean/hand_r → crouch/hand_r
- 0.2167 s：attachment-change arm_r fall-lean/arm_r → crouch/arm_r
- 0.2333 s：attachment-change body fall-lean/body → crouch/body
- 0.2333 s：attachment-change arm_l fall-lean/arm_l → crouch/arm_l
- 0.4333 s：attachment-change cape crouch/cape → brace/cape
- 0.4500 s：attachment-change leg_r crouch/leg_r → brace/leg_r
- 0.4500 s：attachment-change arm_l crouch/arm_l → brace/arm_l

网格风险提示（先确认是否为有意透视/镜像）：
- 0.0000 s：triangle-collapse，cape/fall-lean/cape，三角面 1 个
- 0.0000 s：triangle-collapse，body/fall-lean/body，三角面 1 个
- 0.0167 s：triangle-orientation-flip，body/fall-lean/body，三角面 1 个
- 0.0667 s：triangle-orientation-flip，leg_r/fall-lean/leg_r，三角面 1 个
- 0.0833 s：triangle-orientation-flip，leg_r/fall-lean/leg_r，三角面 1 个
- 0.1833 s：triangle-collapse，leg_r/crouch/leg_r，三角面 1 个
- 0.1833 s：triangle-orientation-flip，leg_r/crouch/leg_r，三角面 1 个
- 0.1833 s：triangle-orientation-flip，arm_l/fall-lean/arm_l，三角面 1 个
- 0.1833 s：triangle-orientation-flip，arm_r/fall-lean/arm_r，三角面 1 个
- 0.2000 s：triangle-orientation-flip，cape/crouch/cape，三角面 1 个
- 0.2000 s：triangle-orientation-flip，leg_l/crouch/leg_l，三角面 1 个
- 0.2000 s：triangle-orientation-flip，leg_r/crouch/leg_r，三角面 1 个

## hit

实际采样 27 帧，有效 FPS 61.905。

最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：
- 当前阈值下无信号；不等于视觉完美。

网格风险提示（先确认是否为有意透视/镜像）：
- 0.0000 s：triangle-collapse，cape/E00/cape，三角面 2 个
- 0.0969 s：triangle-collapse，arm_r/E00/arm_r，三角面 1 个
- 0.1131 s：triangle-orientation-flip，arm_r/E00/arm_r，三角面 1 个
- 0.1292 s：triangle-collapse，cape/E00/cape，三角面 1 个
- 0.1292 s：triangle-orientation-flip，cape/E00/cape，三角面 1 个
- 0.2908 s：triangle-collapse，cape/E00/cape，三角面 1 个
- 0.3069 s：triangle-orientation-flip，cape/E00/cape，三角面 1 个
- 0.3231 s：triangle-collapse，arm_r/E00/arm_r，三角面 1 个
- 0.3231 s：triangle-orientation-flip，arm_r/E00/arm_r，三角面 1 个

## explosion_release

实际采样 43 帧，有效 FPS 60.000。

最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：
- 当前阈值下无信号；不等于视觉完美。

离散事件（独立报告，不自动扣分）：
- 0.3333 s：attachment-change body E12/body → release/body
- 0.3333 s：attachment-change leg_l E12/leg_l → release/leg_l
- 0.3333 s：attachment-change leg_r E12/leg_r → release/leg_r
- 0.3333 s：attachment-change arm_l E12/arm_l → release/arm_l
- 0.3333 s：attachment-change hand_l E12/hand_l → release/hand_l
- 0.3333 s：attachment-change arm_r E12/arm_r → release/arm_r
- 0.3333 s：attachment-change head E12/head → release/head
- 0.3333 s：attachment-change hand_r E12/hand_r → release/hand_r
- 0.4333 s：attachment-change cape E12/cape → release/cape

网格风险提示（先确认是否为有意透视/镜像）：
- 0.0000 s：triangle-collapse，cape/E12/cape，三角面 2 个
- 0.3833 s：triangle-collapse，cape/E12/cape，三角面 1 个
- 0.3833 s：triangle-orientation-flip，cape/E12/cape，三角面 1 个

## chant_enter -> chant_loop

实际采样 31 帧，有效 FPS 60.000。切换时间记作 0；从动画相位 1.300 s，mix=0.200 s。
切换瞬间最大同身份点位置差：0.00000；附件/层序事件 0。

最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：
- 当前阈值下无信号；不等于视觉完美。

网格风险提示（先确认是否为有意透视/镜像）：
- -0.1000 s：triangle-collapse，cape/E12/cape，三角面 2 个

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
