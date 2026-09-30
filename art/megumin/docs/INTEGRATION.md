# 接入说明与坐标约定

## 当前完成范围

这是可独立运行的 Godot 4.6 资源包。旧 Karen 参考仅用于理解 Godot 场景、角色视觉层与死亡替换方式；没有替换其代码，也没有进行 STS2 游戏联调。

## 场景与调用

将 `assets`、`animations`、`scenes/megumin.tscn` 和 `scripts/megumin_rig.gd` 放到目标工程对应路径，或同步修改资源引用路径。

```gdscript
var visuals: MeguminRig = preload("res://scenes/megumin.tscn").instantiate()
add_child(visuals)
visuals.position = ground_position
visuals.scale = Vector2.ONE * (320.0 / 1482.0)
visuals.effects_enabled = false
visuals.attack_impact.connect(on_attack_impact)
visuals.play_animation("Cast")
```

`play_animation(state)` 返回 bool：有效状态为 true，未知状态或死亡锁定后尝试普通动作返回 false。

支持的名称及别名：

- `Idle` / `idle`
- `Cast` / `cast` / `casting`
- `Attack` / `attack`
- `Hit` / `hit` / `hurt`
- `Relaxed` / `relaxed` / `exhausted`
- `Dead` / `dead` / `death`

方法：`reset_character()`、`play_animation(state)`

信号：

- `animation_state_changed(state)`：动作被接受并开始
- `animation_completed(state)`：单次动作结束
- `attack_impact`：Attack 时间轴 0.72 秒处，单次发出
- `marker_reached("damage")`：相同伤害时点的带名称接口

如果目标工程使用 C#，可以通过 Godot 的 `Call("play_animation", "Attack")` 和 `Connect("attack_impact", ...)` 访问该 GDScript 场景；实际挂接到 `NCreatureVisuals` 的方式需按目标工程确认。

## 伤害与游戏逻辑

本包只发出信号，不修改血量。未实现跨回合的持续预备玩法状态；Cast 当前为固定时长演示动画。附带光束只是时点和方向示意，不是最终爆炸 VFX。请由现有战斗系统决定伤害执行方式：

- 事件驱动接法：监听 `attack_impact` 并在该点触发已授权的伤害/VFX
- 延时接法：Attack 起播后 0.72 秒匹配当前资源的冲击帧

旧 Karen 参考中的 `AttackAnimDelay = 0.15` 与本动画不一致，不能直接沿用。使用 `animation_speed` 调速时，现实时间中的冲击时点为 `0.72 / animation_speed`。不要同时接事件和延时两条伤害路径，避免重复结算。

## 地面锚点与画布

源母图坐标：1024 × 1536。角色源坐标原点采用 `(575, 1508)`，位于左靴最低落地基准；源坐标减去此点得到场景局部坐标。场景的 Node2D 原点就是落地锚点。右脚保持原插画透视的较高位置。

最终静态图：1600 × 1760。对应锚点 `(760, 1640)`。

若以 Sprite2D 使用静态图：

```gdscript
sprite.centered = false
sprite.position = Vector2(-760, -1640) * sprite.scale
```

若 Sprite2D 使用 `centered = true`，则纹理中心到锚点的偏移为 `(40, -760)`，同样乘以缩放。

右侧游戏尺寸检查使用固定缩放 `320/1482 ≈ 0.215924`，整个序列不按每帧 bounding box 重算比例。跪姿和倒地姿态因此自然变矮，不会被拉大。

专用姿态配准：

- Relaxed 源画布1536 × 1024；源锚点 `(900, 998)`，相对站立源单位缩放0.94
- Dead 源画布1536 × 1024；源锚点 `(810, 790)`，相对站立源单位缩放0.88

## 编辑关节与网格

`megumin.tscn` 内已有原生 AnimationPlayer 和 AnimationLibrary，时间轴资源位于 `animations/`，可以直接在 Godot 编辑器打开并改关键帧。

关节在母图坐标中定义：腰 `(619,701)`、颈 `(583,498)`、自由侧肩 `(484,539)` / 肘 `(444,631)`、持杖侧肩 `(674,545)` / 肘 `(740,631)` / 握点 `(875,588)`。

角色分件由 `assets/rig_geometry.json` 在运行时生成 Polygon2D。每一分件保存未改变的源纹理 UV 和可变形顶点；披风使用内部三角网格。几何生成脚本 `tools_build.py` 依赖 SciPy，只在要重建配置时才需要运行。

## 建议游戏内验收

尚需在目标 STS2 工程确认：资源目录、坐标与缩放、角色朝向、视觉层级、特效遮挡、攻击时点、受击打断、死亡生命周期，以及战斗结束/重新入场时的 reset 调用。当前自动验收仅覆盖本独立工程。
