# 惠惠 v6 · 五状态动画交付

以用户批准的官方风格、朝画面右侧三分之四立绘重新制作。当前完成 **Idle / Cast / Attack / Hit / Relaxed**；**Dead 未完成**，实验姿态不作为可用死亡动画。旧版本与阶段快照保留。

## 观看

`preview/megumin_v6_five_states_review.mp4`：1440×960，30fps，581帧，19.366667秒，固定大画面与320px角色参照并排，无特效。

| 视频时间 | 状态 | 内容 |
|---|---|---|
| 0–3.00s | Idle | 自然稳站、轻微呼吸与披风跟随 |
| 3.00–7.80s | Cast | 抬肘举杖、吟唱停顿、收回 |
| 7.80–15.00s | Attack | 蓄力、举杖、向右释放、脱力恢复 |
| 15.00–15.95s | Hit | 肩胸后仰与跟随、回站 |
| 15.95–19.35s | Relaxed | 头肩躯干疲惫下沉、恢复 |

精确关键姿势与每状态拼图在 `preview/five_states/key_*.png` 和 `contact_*.png`。腿修前后对照在 `preview/legmotion_fix/`。

**视频是Godot真实AnimationPlayer/Polygon2D时间轴导出后的离线软件光栅预览。不是Godot图形窗口录像，也没有完成STS2游戏内加载/伤害时点验证。** 数值、采样静帧检查和原速播放审阅分别记录，不把测试通过等同人体动作正确。

## 已实现约束

- 批准原图头脸/手保持同源，固定骨段长度，右手持杖及右腿白绷带/左腿深袜不交换
- 从裙内髋到膝到靴内真实踝重新标记；靴筒随胫骨，踝下足部支持
- 主链保持自然稳站，仅极小合理微屈；已去掉早期双膝外撑与过大髋下沉
- 连续FK/IK与局部网格关节动作，无全姿态纹理硬切、无透明交叉淡化
- 补底只修被遮住的服装区域，配准到批准母图；腿/杖/袖误带像素与帽沿层次已修
- 原图及五张必要补底经过专用去摩尔纹检测与原尺寸目视：未见支持的周期伪影，保原；未强行平滑或损伤alpha/线稿

## 工程使用

Godot 4.6.x打开 `project.godot`，主场景 `scenes/preview.tscn`，角色场景 `scenes/megumin.tscn`。

运行已有工程不依赖其他版本。工具需要Python、NumPy、SciPy、Pillow；重录视频需ffmpeg。离线预览排版还使用系统DejaVu Sans字体（Linux默认路径）；其他平台可改渲染脚本的字体路径，这不影响Godot角色场景运行。

- 主链复验：`bash tools/run_tests.sh`
- 五状态几何导出：`godot --headless --path . --script scripts/export_five_states_review.gd`
- 五状态数值复验：`python tools/test_five_states_review.py --no-images`
- 完整原速重新渲染：`bash tools/run_five_states_review.sh`
- 从包内源重新构建：`python tools/build_v6.py`、`python tools/build_timeline.py`、`python tools/build_states_v6.py`

`play_state()`接受已制作状态，非Idle结束回Idle。Attack建议impact事件在该状态3.50s发出，是否对应游戏伤害需要后续接入验证。`Dead`没有可用动作资源，不能用旧实验文件充数。

## 边界与未完成

- 现有固定3/4视角二维cutout仍存在平面感，不是可任意旋转的3D角色
- 主链及五状态已做数值与列明采样静帧验收；未在图形播放器逐帧看完整片，不称原速节奏已获最终批准
- 不含爆炸VFX或STS2脚本接入
- Dead深跪缺少侧后膝/靴视角且局部折叠不自然，有限替代仍像扶杖昏厥，故明确未完成，详见 `docs/DEAD_LIMITATION.md`
- `animations/Dead_unreviewed_legacy.tres`和`preview/dead_probe`若保留，仅属未验实验历史，不加载为成品

验证结果见 `tests/five_states_validation.json`、`tests/legmotion_fix_validation.json`、`tests/legmotion_fix_continuity.json`；静帧记录见 `docs/INDEPENDENT_VISUAL_QA.md`与`tests/five_states_visual_review.md`。角色及官方参考权利归原权利方，本工程是AI辅助同人mod素材，不称官方素材授权发布。
