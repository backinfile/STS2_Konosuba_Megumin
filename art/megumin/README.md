# 惠惠 · 爆裂魔法动画资源 v1

独立 Godot 4.6 动画工程。包含同源立绘分件、六状态动画、透明站立终稿、原速预览和自动测试。**尚未接入或验证 STS2 游戏工程**。

## 快速打开

1. 用 Godot 4.6.x 打开 `project.godot`
2. 按 F6/F5 运行 `scenes/preview.tscn`，会以原速播放六个状态
3. 键盘 1–6 或下方按钮单独切换；空格重播完整演示
4. 左侧是大尺寸检查，右侧保持约 320 px 的常态人物高度

无需第三方插件、.NET、Spine 或 Python 就能运行。Python + SciPy 仅用于重新生成几何配置，不是游戏运行依赖。

## 文件入口

- `assets/runtime/megumin_idle_neutral.png`：最终可用透明站立图，1600 × 1760，完整法杖有留白
- `scenes/megumin.tscn`：可实例化角色场景，内置原生 AnimationPlayer
- `animations/*.tres`：六个可编辑的原生 Godot Animation 资源
- `scripts/megumin_rig.gd`：关节、披风网格、状态控制与接口
- `assets/rig_geometry.json`：16 个源纹理分件的顶点、UV、层级和分组
- `assets/source/`：未经改写的 imagegen 母图、去遮挡补底、完整法杖
- `assets/poses/`：独立脱力跪姿和倒地姿态原图
- `preview/megumin_reel.mp4`：1440 × 900，30 fps，约 21.13 秒，原速六状态预览
- `preview/key_*.png`：六状态关键帧
- `tests/results.json`、`tests/godot_test.log`：自动验收记录
- `docs/INTEGRATION.md`：接入、锚点、事件与状态映射

## 动作说明

| 状态 | 时长 | 行为 |
|---|---:|---|
| Idle | 3.0 s 循环 | 胸肩呼吸、头部轻动、左右臂细动、独立披风波动；脚底固定 |
| Cast | 2.6 s | 左上臂、前臂分别转动，抬手咏唱，杖随持杖臂倾斜，魔法环蓄能 |
| Attack | 1.9 s | 预备、前倾和朝右爆裂；0.72 s 发出伤害时点信号 |
| Hit | 0.66 s | 上身、头和双臂短促后仰，局部闪色，恢复原位 |
| Relaxed | 4.8 s | 下沉后切换专用跪姿，轻微呼吸，站起回待机 |
| Dead | 1.6 s | 受挫下沉后切换专用倒地图，终态保持 |

当前只实现动画播放状态机，未实现玩法逻辑或可跨回合的无限持续预备状态。Cast 的 2.6 秒后回 Idle 是演示行为；若目标玩法需要持续预备，需在接入时另加保持/循环状态。

除 Dead 外，单次动作结束默认回到 Idle。Dead 必须显式调用 `reset_character()` 才能重新站立。

Relaxed/Dead 是关节起始过渡加专用姿态切换，不是逐帧全骨骼下跪/倒地模拟。其专用画面按脸部和帽子比例配准，未将横幅图片强压成竖幅。

## 美术与可调范围

站立动作使用帽脸、躯干补底、裙腿、左右臂、持杖手、完整法杖和披风独立分件；没有把一张完整人物图整体摇晃作为动作。腿部保持固定，披风顶端跟随肩部、下摆独立网格变形。

胸腹被原手臂遮住的位置使用同人物的去遮挡重绘；原披风里被手臂挡住的区域使用母图完好布料的 UV 补底。原 PNG 的透明通道和像素未被重新绘制或归一化。完整杖图按宝珠直径与轴线配准，握点与手部使用同一变换链。

在动画资源里修改 `left_upper`、`left_forearm`、`right_upper`、`right_forearm`、`grip_tilt` 等角度轨道即可调姿势。超出当前动作幅度的大幅旋转可能需要补画新的遮挡区域，避免直接拉大角度造成穿帮。当前是首版 cutout art study，320 px 尺寸已目视检查；高倍检视仍可见个别 UV 补底连接，后续可继续做美术级细化。

`effects_enabled = false` 可关闭附带的魔法环和光束。当前朝右光束只是独立预览的演示 VFX，并非最终爆裂爆炸效果，也不承担游戏伤害逻辑。

## 验证与重新输出

- 图形验证：Godot 4.6.3，Compatibility / llvmpipe，实际渲染六状态视频
- 功能测试：`godot --headless --path . --script tests/test_rig.gd`
- 重新导出透明终稿：运行 `scenes/export_runtime.tscn`
- 在已有桌面图形会话中复现视频：`./render_preview.sh`，需要 Godot 与 ffmpeg；脚本不会新建显示服务器或网络监听
- 纯 headless 环境可运行逻辑测试，但重新录制需要本地图形会话；本包已附渲染完成的 MP4
- 完整测试入口：`tools/run_tests.sh`

云端虚拟显卡可能打印“V-Sync 不支持”的提示，不影响固定 30 fps 电影输出。最终日志不含脚本/渲染错误。

角色基于《为美好的世界献上祝福！》惠惠的同人表现；本包不包含角色 IP 授权声明。
