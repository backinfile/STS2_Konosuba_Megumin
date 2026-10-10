# Spine 连续性风险检查

输入：synthetic.json · Spine 4.2.43 · runtime 4.2.120
参考长度：28.28427 (setup-visible geometry bounding-box diagonal (before clipping/occlusion))
采样：请求 60 FPS；物理：none；可见网格每附件最多 16 个顶点。

速度、加速度和 jerk 均已按固定参考长度归一化。风险计数是“点×时间×指标”的诊断数量，不是缺陷数量，也不能当分数排名。

## 汇总

| 动画/过渡 | 时长 s | 风险信号 | 已标注意图 | 附件/层序等事件 | 网格提示 | loop位置差 | loop速度差 |
|---|---:|---:|---:|---:|---:|---:|---:|
| stationary | 1.000 | 0 | 0 | 0 | 0 | n/a | n/a |
| constant_velocity | 1.000 | 0 | 0 | 0 | 0 | n/a | n/a |
| constant_velocity_long | 2.000 | 0 | 0 | 0 | 0 | n/a | n/a |
| constant_velocity_short | 1.013 | 0 | 0 | 0 | 0 | n/a | n/a |
| closed_velocity_kink | 1.000 | 30 | 0 | 0 | 0 | 0.00000 | 7.07107 |
| stepped_jump | 1.000 | 70 | 0 | 0 | 0 | n/a | n/a |
| cusp | 1.000 | 30 | 0 | 0 | 0 | n/a | n/a |
| smooth_loop | 1.000 | 0 | 0 | 0 | 0 | 0.00000 | 0.00003 |
| rotation_across_world_wrap | 1.000 | 0 | 0 | 0 | 0 | n/a | n/a |
| genuine_spin | 1.000 | 0 | 0 | 0 | 0 | n/a | n/a |
| aliasing_spin | 0.100 | 0 | 0 | 0 | 0 | n/a | n/a |
| zero_duration | 0.000 | 0 | 0 | 0 | 0 | n/a | n/a |
| from_a | 1.000 | 0 | 0 | 0 | 0 | n/a | n/a |
| to_b | 1.000 | 0 | 0 | 0 | 0 | n/a | n/a |
| attachment_swap | 1.000 | 0 | 0 | 1 | 0 | n/a | n/a |
| attachment_hide | 1.000 | 0 | 0 | 2 | 0 | n/a | n/a |
| deform_only | 1.000 | 3 | 0 | 0 | 0 | n/a | n/a |
| from_a -> to_b | 0.500 | 300 | 0 | 0 | 0 | n/a | n/a |

## stationary

实际采样 61 帧，有效 FPS 60.000。

最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：
- 当前阈值下无信号；不等于视觉完美。

## constant_velocity

实际采样 61 帧，有效 FPS 60.000。

最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：
- 当前阈值下无信号；不等于视觉完美。

## constant_velocity_long

实际采样 121 帧，有效 FPS 60.000。

最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：
- 当前阈值下无信号；不等于视觉完美。

## constant_velocity_short

实际采样 62 帧，有效 FPS 60.217。

最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：
- 当前阈值下无信号；不等于视觉完美。

## closed_velocity_kink

实际采样 61 帧，有效 FPS 60.000。
仅在准备循环播放时解读：端点位置风险 false，端点速度风险 true；附件/层序接缝事件 0。速度采用5点高阶单侧差分，对比3点结果估计误差：0.00005；误差估计不是严格界限，需提高FPS复验。

最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：
- 0.5083 s [0.4833, 0.5333]：jerk=25456.03834，阈值=3000.00000；slot:art/quad#default/quad/v0
- 0.5083 s [0.4833, 0.5333]：jerk=25456.03834，阈值=3000.00000；slot:art/quad#default/quad/v3
- 0.4917 s [0.4667, 0.5167]：jerk=25456.03834，阈值=3000.00000；slot:art/quad#default/quad/v0
- 0.4917 s [0.4667, 0.5167]：jerk=25456.03834，阈值=3000.00000；slot:art/quad#default/quad/v3
- 0.5083 s [0.4833, 0.5333]：jerk=25456.03834，阈值=3000.00000；slot:art/quad#default/quad/v1
- 0.5083 s [0.4833, 0.5333]：jerk=25456.03834，阈值=3000.00000；slot:art/quad#default/quad/v2
- 0.4917 s [0.4667, 0.5167]：jerk=25456.03834，阈值=3000.00000；slot:art/quad#default/quad/v1
- 0.4917 s [0.4667, 0.5167]：jerk=25456.03834，阈值=3000.00000；slot:art/quad#default/quad/v2
- 0.5083 s [0.4833, 0.5333]：jerk=25455.84412，阈值=3000.00000；bone:tip/origin
- 0.5083 s [0.4833, 0.5333]：jerk=25455.84412，阈值=3000.00000；bone:tip/y-axis
- 0.4917 s [0.4667, 0.5167]：jerk=25455.84412，阈值=3000.00000；bone:tip/origin
- 0.4917 s [0.4667, 0.5167]：jerk=25455.84412，阈值=3000.00000；bone:tip/y-axis

## stepped_jump

实际采样 61 帧，有效 FPS 60.000。

最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：
- 0.4917 s [0.4667, 0.5167]：jerk=1527350.64736，阈值=3000.00000；bone:tip/y-axis
- 0.4917 s [0.4667, 0.5167]：jerk=1527350.64736，阈值=3000.00000；slot:art/quad#default/quad/v0
- 0.4917 s [0.4667, 0.5167]：jerk=1527350.64736，阈值=3000.00000；slot:art/quad#default/quad/v1
- 0.4917 s [0.4667, 0.5167]：jerk=1527350.64736，阈值=3000.00000；slot:art/quad#default/quad/v2
- 0.4917 s [0.4667, 0.5167]：jerk=1527350.64736，阈值=3000.00000；slot:art/quad#default/quad/v3
- 0.4917 s [0.4667, 0.5167]：jerk=1527350.64736，阈值=3000.00000；bone:root/origin
- 0.4917 s [0.4667, 0.5167]：jerk=1527350.64736，阈值=3000.00000；bone:root/x-axis
- 0.4917 s [0.4667, 0.5167]：jerk=1527350.64736，阈值=3000.00000；bone:root/y-axis
- 0.4917 s [0.4667, 0.5167]：jerk=1527350.64736，阈值=3000.00000；bone:tip/origin
- 0.4917 s [0.4667, 0.5167]：jerk=1527350.64736，阈值=3000.00000；bone:tip/x-axis
- 0.5083 s [0.4833, 0.5333]：jerk=763675.32368，阈值=3000.00000；bone:tip/y-axis
- 0.5083 s [0.4833, 0.5333]：jerk=763675.32368，阈值=3000.00000；slot:art/quad#default/quad/v0

## cusp

实际采样 61 帧，有效 FPS 60.000。

最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：
- 0.5083 s [0.4833, 0.5333]：jerk=50911.68825，阈值=3000.00000；bone:root/x-axis
- 0.5083 s [0.4833, 0.5333]：jerk=50911.68825，阈值=3000.00000；bone:root/y-axis
- 0.4917 s [0.4667, 0.5167]：jerk=50911.68825，阈值=3000.00000；bone:root/x-axis
- 0.4917 s [0.4667, 0.5167]：jerk=50911.68825，阈值=3000.00000；bone:root/y-axis
- 0.5083 s [0.4833, 0.5333]：jerk=50911.68825，阈值=3000.00000；bone:tip/x-axis
- 0.5083 s [0.4833, 0.5333]：jerk=50911.68825，阈值=3000.00000；bone:tip/y-axis
- 0.5083 s [0.4833, 0.5333]：jerk=50911.68825，阈值=3000.00000；bone:root/origin
- 0.4917 s [0.4667, 0.5167]：jerk=50911.68825，阈值=3000.00000；bone:root/origin
- 0.4917 s [0.4667, 0.5167]：jerk=50911.68825，阈值=3000.00000；bone:tip/x-axis
- 0.4917 s [0.4667, 0.5167]：jerk=50911.68825，阈值=3000.00000；bone:tip/y-axis
- 0.5083 s [0.4833, 0.5333]：jerk=50911.68825，阈值=3000.00000；bone:tip/origin
- 0.4917 s [0.4667, 0.5167]：jerk=50911.68825，阈值=3000.00000；bone:tip/origin

## smooth_loop

实际采样 61 帧，有效 FPS 60.000。
仅在准备循环播放时解读：端点位置风险 false，端点速度风险 false；附件/层序接缝事件 0。速度采用5点高阶单侧差分，对比3点结果估计误差：0.03260；误差估计不是严格界限，需提高FPS复验。

最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：
- 当前阈值下无信号；不等于视觉完美。

## rotation_across_world_wrap

实际采样 61 帧，有效 FPS 60.000。

最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：
- 当前阈值下无信号；不等于视觉完美。

## genuine_spin

实际采样 61 帧，有效 FPS 60.000。

最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：
- 当前阈值下无信号；不等于视觉完美。

## aliasing_spin

实际采样 8 帧，有效 FPS 70.000。

最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：
- 当前阈值下无信号；不等于视觉完美。

角度欠采样警告：
- root，0.0000–0.1000 s：平均每采样步约 514.3 度，当前结果可能把快速转动误读成静止。

## zero_duration

实际采样 1 帧，有效 FPS n/a。

最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：
- 当前阈值下无信号；不等于视觉完美。

## from_a

实际采样 61 帧，有效 FPS 60.000。

最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：
- 当前阈值下无信号；不等于视觉完美。

## to_b

实际采样 61 帧，有效 FPS 60.000。

最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：
- 当前阈值下无信号；不等于视觉完美。

## attachment_swap

实际采样 61 帧，有效 FPS 60.000。

最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：
- 当前阈值下无信号；不等于视觉完美。

离散事件（独立报告，不自动扣分）：
- 0.5000 s：attachment-change art quad → alternative

## attachment_hide

实际采样 61 帧，有效 FPS 60.000。

最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：
- 当前阈值下无信号；不等于视觉完美。

离散事件（独立报告，不自动扣分）：
- 0.5000 s：attachment-change art quad →
- 0.5000 s：visibility-change art true → false

## deform_only

实际采样 61 帧，有效 FPS 60.000。

最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：
- 0.5083 s [0.4833, 0.5333]：jerk=25456.03834，阈值=3000.00000；slot:art/quad#default/quad/v2
- 0.4917 s [0.4667, 0.5167]：jerk=25456.03834，阈值=3000.00000；slot:art/quad#default/quad/v2
- 0.5000 s [0.4833, 0.5167]：acceleration=424.26536，阈值=60.00000；slot:art/quad#default/quad/v2

## from_a -> to_b

实际采样 31 帧，有效 FPS 60.000。切换时间记作 0；从动画相位 0.250 s，mix=0.200 s。
切换瞬间最大同身份点位置差：0.00000；附件/层序事件 0。

最强连续性风险信号（完整逐帧数据和全部点见 JSON/CSV）：
- 0.2083 s [0.1833, 0.2333]：jerk=111369.62878，阈值=3000.00000；slot:art/quad#default/quad/v1
- 0.2083 s [0.1833, 0.2333]：jerk=111369.62878，阈值=3000.00000；slot:art/quad#default/quad/v2
- 0.2083 s [0.1833, 0.2333]：jerk=111369.62878，阈值=3000.00000；slot:art/quad#default/quad/v0
- 0.2083 s [0.1833, 0.2333]：jerk=111369.62878，阈值=3000.00000；slot:art/quad#default/quad/v3
- 0.1917 s [0.1667, 0.2167]：jerk=111369.39572，阈值=3000.00000；slot:art/quad#default/quad/v1
- 0.1917 s [0.1667, 0.2167]：jerk=111369.39572，阈值=3000.00000；slot:art/quad#default/quad/v2
- -0.0083 s [-0.0333, 0.0167]：jerk=111369.39572，阈值=3000.00000；slot:art/quad#default/quad/v0
- -0.0083 s [-0.0333, 0.0167]：jerk=111369.39572，阈值=3000.00000；slot:art/quad#default/quad/v3
- 0.1917 s [0.1667, 0.2167]：jerk=111369.39572，阈值=3000.00000；slot:art/quad#default/quad/v0
- 0.1917 s [0.1667, 0.2167]：jerk=111369.39572，阈值=3000.00000；slot:art/quad#default/quad/v3
- 0.0083 s [-0.0167, 0.0333]：jerk=111369.33746，阈值=3000.00000；slot:art/quad#default/quad/v0
- 0.0083 s [-0.0167, 0.0333]：jerk=111369.33746，阈值=3000.00000；slot:art/quad#default/quad/v3

## 可信范围与限制

- Continuity risk signals are review candidates, not an aesthetic score or universal quality standard. Deliberate impacts/holds can produce strong signals.
- Geometry only: no pixels/textures, silhouette matching across attachment swaps, perceptual salience, occlusion, clipping, anti-aliasing, camera motion or real frame pacing.
- Single skeleton, skin and track 0 only. Match production tracks, timeScale, mix configuration, interruptions and engine behavior separately.
- Finite sampling can miss subframe jumps or alias fast rotations (especially >=180 degrees/sample). Verify suspect times at 2x/4x FPS.
- Derivative magnitudes depend on FPS around actual discontinuities; compare identical settings. Quantiles pool landmarks, so rig density can bias cross-character comparisons.
- Bone probes include helper bones by default; use visible-geometry summaries, --visible-bones-only or bone filters. Bone influence is a dependency approximation, not pixel visibility.
- Triangle collapse/flip is a geometric hint, not proof of a rendering defect. First visible pose is the reference and may already be distorted.
- No atlas: region corners skipped to avoid incorrect trim/rotation geometry. Mesh vertices and bones still sampled. Supply matching .atlas for complete region landmarks.

## 下一步

1. 先看 visible-geometry 与具体 slot/bone；再看被标记区间和附件事件。
2. 用相同设置在 60/120/240 FPS 复验；真实阶跃的导数通常随 FPS 增长，有限差分噪声也会变大。
3. 在原播放器逐帧检查命中/急停/换姿势是否有意；用 config.suppressions 标注意图，保留审计记录。
4. loop 要同时检查位置与速度；实际切换必须用运行时 mix 配置模拟，端点相等并不能保证中段无褶皱或像素跳。
