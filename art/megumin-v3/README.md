# 惠惠 v3 · 连续骨骼小样

当前交付为腿连接修正版，已独立锁包。新片 `preview/megumin_continuous_v3_legfix.mp4`；旧片 `preview/megumin_continuous_v3.mp4` 保持冻结，具体诊断与对照见 `docs/LEG_CONNECTION_REVIEW.md`。

本轮是 **5.4 秒、无 VFX 的连续动作审核小样**，不是六状态终版。v1 / v2 保持冻结。

## 先看这里

- `preview/megumin_continuous_v3_legfix.mp4`：1440×960，30fps，原速 5.433 秒（含 0.0–5.4 秒共 163 帧），固定大画面与约 320px 常态人物参照并列
- `scenes/preview.tscn`：Godot 实时预览，含拖动时间轴、暂停和重播
- `scenes/megumin.tscn`：独立角色场景
- `animations/ContinuousCast.tres`：12 条原生可编辑 AnimationPlayer 数值轨道
- `animations/art_directed_keys.json`：10 个主要姿势控制点；构建脚本以最小 jerk 缓动采样为 60Hz 数值轨道，运行时保持连续插值
- `tests/continuous_validation.json`：59 项自动不变量检查及尺寸测量
- `tests/timeline_continuity.json`：8 处主要阶段边界的亚帧连续性检查

## 动作与约束

自然站姿 → 预备负重 → 抬肘 → 高举吟唱 → 快速释放 → 回收 → 短暂屈膝、头肩下沉 → 回自然站姿。

- 同一母图的头帽、左右手、上臂/前臂、腿段、靴、完整法杖贯穿全片
- 不切换全身姿态图、不淡入淡出、不重画每帧头脸或手
- 头帽是一个刚性分件；头部朝向固定为原图的朝右 3/4 视角
- 肩、肘、腕为 FK 层级，腕和法杖共用同一变换链
- 髋部位移和下沉驱动两段腿 IK；膝关节变化，靴及足底不移动
- 起止 Idle 两膝均约 8° 微松，蓄力才屈膝。骨盆转轴为两髋中心 (614,852)，自然站姿髋上移16.688px并侧倾8.531°，躯干反向补偿；没有缩腿来凑脚距
- 头、手、双臂、靴和骨节点只平移/旋转，缩放始终为 1；腿部仅膝周与裙下髋附着带采用同源连续UV旋转混合，远端骨段仍刚性；左袖下摆独立旋转，披风柔变
- 相机固定；大图比例 0.42，参照比例 320/1398，全片不自动缩放角色

这是基于 Node2D FK/IK 层级的混合 rig。头手臂靴保持刚性，腿的窄关节带采用连续旋转蒙皮，骨长度不变；不使用全身姿态替换。

## 基准尺寸（母图坐标 px）

| 项目 | 固定尺寸 |
|---|---:|
| 足底锚点横距 | v1 553 → v3 453，收窄约 18.1% |
| 头帽分件原始 bbox | 610 × 393 |
| 左上臂 / 前臂骨长 | 115.000 / 83.522 |
| 右上臂 / 前臂骨长 | 108.407 / 91.679 |
| 左手部纹理分件 bbox | 115.687 × 119.915 |
| 右手部纹理分件 bbox | 102 × 100 |
| 左大腿 / 小腿骨长 | 221.923 / 222.092 |
| 右大腿 / 小腿骨长 | 205.730 / 191.324 |
| 左靴裁切 bbox | 195.802 × 301 |
| 右靴裁切 bbox | 197.356 × 266 |
| 完整法杖可见端到端长度 | 1276.274 |

bbox 指原始分件的裁切坐标边界，不是旋转后的屏幕 AABB。法杖沿用 v1 一次性 0.83 配准；运行时完全不缩放。手部 bbox 包含掌、指和手套/腕交界，不是纯掌骨大小。

## 验证结果与范围

Godot 4.6.3 headless 运行了真实 AnimationPlayer / Polygon2D 并导出每帧顶点、UV 和全局变换。59 项约束全部通过：每帧同一分件、固定刚性形状、固定骨长、零足底漂移、全杖刚性、同链握点、无姿态 alpha 混合、v1 源图逐字节不变。

8 处阶段边界在 ±0.0001 秒两侧采样，最大顶点距离仅 0.00927px，未发现跳帧式切换。原生预览场景可正常加载并 tick。

**所附 MP4 是 Godot 导出几何的离线软件光栅预览，不是 Godot 图形窗口实录。** 当前云环境无法创建显示会话，因此没有声称完成引擎 framebuffer 的图形验收。项目可在有正常显示会话的 Godot 4.6.x 中实时运行。

## 本轮仍可见的美术限制

- 领口和腋下破洞已通过同源头部精裁、固定胸肩补底和层次整理修复；高倍仍可辨认 cutout 交界
- 左袖下摆增加固定尺寸的重力朝向跟随，保持下垂；右宽袖仍保留平面 cutout 的折片风格
- 腿连接修正版已移除圆形膝盖盖片，改用连续UV；裙边与靴口误带的腿部像素也已清理，高倍仍能观察到局部纹理弯曲
- 释放前倾和末态垂头幅度克制，未以拉长、压扁身体换取夸张动作
- 表情、头部视角固定；当前没有喊招口型、换向、全身倒地或六状态 API
- 尚未接入或验证 STS2 游戏工程

## 重新生成

无需 Python 即可用 Godot 打开和运行已有工程。Python 工具只用于重新生成或审核素材几何。

```bash
python tools/build_continuous.py
./tools/run_tests.sh
python tools/render_software_review.py --parallel
ffmpeg -y -framerate 30 -i preview/software/frame_%04d.png -c:v libx264 -crf 18 -pix_fmt yuv420p -movflags +faststart preview/megumin_continuous_v3_legfix_rebuilt.mp4
```

Python 工具使用 NumPy、SciPy、Pillow。构建所需基准已包含在 assets/baseline，无需另下载 v1。当前包提供源资源、Godot 场景、验证结果和预览，发布由独立流程管理。

`tools/leg_review_compare.py` 是历史对照图的维护脚本，需要另存的 bf0e567 快照；一般使用者无需运行它。交付包已含生成好的对照 PNG。
