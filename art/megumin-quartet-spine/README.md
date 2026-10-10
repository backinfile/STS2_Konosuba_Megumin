# 惠惠 · 四重奏风格 Spine 动作样机 v0.1

**最新动作复查：[Actions v9 参考 / Spine 对照](actions-v9/preview.html) · [v9 制作说明](actions-v9/README.md) · [导入包](actions-v9/megumin-actions-v9-import.zip) · [Spine 制作指引](../../docs/Spine动画制作指引.md)**。13 套参考姿势、19 个动作；保留 v8 的体积校准，新增连续速度、曲线路径与身体跟随。Spine 编辑器导入尚未实测。

[v8](actions-v8/preview.html)、[v7](actions-v7/preview.html)、[v6](actions-v6/preview.html)、[F00–F72 旧规划](chant-enter-plan/index.html)、[v5](actions-v5/preview.html)、[v4](actions-v4/preview.html) 保留作历史比较。最新数据位于 `actions-v9/export/`。下文是历史 v1 样机记录。

2026-10-09。16 根骨骼、12 个插槽、18 个有效绘图附件、双臂 IK、18 个动画片段。

这是实际 Spine 4.2 JSON 骨骼动画，由官方 Spine WebGL 4.2.95 运行库播放。尚未接入 STS2 游戏，也不是经过 Spine 编辑器保存的 `.spine` 工程或二进制 `.skel`。本机未找到 Spine 编辑器；现有 MegaDot 的独立运行环境也没有注册 Spine 类，因此本次没有宣称通过原生 Godot 或游戏运行验证。

## 查看

- **直接打开 `preview.html`**：包含运行库、数据和纹理，无需联网、安装依赖或启动服务。
- `index.html`：开发版，需要 HTTP 服务。在本目录运行 `py -m http.server 11151 --bind 127.0.0.1`，访问 `http://127.0.0.1:11151/`。
- 预览有完整演示、状态按钮、单片段选择、暂停拖帧、慢放、骨骼/握点显示和 320 px 观察尺寸。
- `megumin-spine-import.zip`：供编辑器导入的 JSON、图片和图集打包。

## 使用了哪些现有参考

1. 当前项目 `art/megumin-v6/`：参考已有动作命名、呼吸克制、固定落脚点和动作连续性思路；没有替换或修改 v6。
2. 当前项目 `art/isekai-quartet-references-20261009/index.html`：主要参考 A02 双手朝右持杖、A05 仰躺脱力、A07 短手势、A09 右手持杖。剧照只提供姿态依据，时间与中间过程为本次设计。
3. `D:/Github/WatcherMod/Watcher/animation/watcher.spskel`：检查二进制头确认其 Spine 版本为 **4.2.11**；参考同目录 `watcher_skel_data.tres`、`watcher_node.tscn` 的 SpineSprite 和资源组织方式。没有复制其人物绘图或动画数据。
4. `D:/Github/spire-codex/extraction/raw/src/Core/Animation/CreatureAnimator.cs`：确认游戏使用 `Idle / Attack / Cast / Hit / Dead / Revive` 等触发名，动画名与触发名分开，并可配置循环和后续状态。
5. 同源码 `Core/Bindings/MegaSpine/SpineAnimationAccess.cs`：参考设置、排队和读取轨道动画的接口。未把独立预览中的计时器当作游戏接入代码。

格式依据：[Spine JSON](https://esotericsoftware.com/spine-json-format)、[编辑器导入](https://esotericsoftware.com/spine-import)、[Godot 官方运行库](https://en.esotericsoftware.com/spine-godot)。运行库与编辑器需要匹配 4.2 系列。Godot JSON 导出副本使用 `.spine-json` 后缀。

## 动作清单与接入关系

| 片段 | 时长 | 用途 / 下一状态 |
|---|---:|---|
| `idle_loop` | 3.00 s 循环 | 固定双脚与法杖，微呼吸、眨眼 |
| `cast_short` | 0.65 s | 普通施放 → 待机 |
| `chant_enter` | 0.60 s | 搭杖 → `chant_loop` |
| `chant_loop` | 2.00 s 循环 | 持续吟唱，等待玩法事件 |
| `chant_cancel` | 0.45 s | 取消吟唱 → 待机 |
| `chant_ack` | 0.50 s | 吟唱中出牌 → `chant_loop` |
| `attack_short` | 0.65 s | 普通出招 → 待机；0.27 s 有 `impact` 标记 |
| `explosion_release` | 0.60 s | 一次身体释放；0.40 s 有 `release` 标记 |
| `explosion_hold` | 0.60 s 循环 | 保持到本轮多段伤害结算完成 |
| `explosion_exit` | 0.35 s | 卸力 → `relaxed_fall` |
| `hit` | 0.40 s | 站立受击 → 待机 |
| `hit_chant` | 0.40 s | 吟唱中受击 → `chant_loop` |
| `relaxed_fall` | 0.80 s | 腿软 → 坐下 → 仰躺 |
| `relaxed_loop` | 2.00 s 循环 | 脱力保持；不代表禁止出牌的规则 |
| `get_up` | 0.95 s | 仰躺 → 坐起 → 站姿 |
| `dead` | 0.90 s | 从站立侧倒，最后一帧保持 |
| `dead_from_down` | 0.35 s | 已倒地时死亡，避免先站起 |
| `hit_down` | 0.28 s | 倒地受击 → `relaxed_loop` |

接入时应保留“当前基础状态”为待机、吟唱、倒地或死亡。不要把所有短动作统一排队回 `idle_loop`；不要对每个敌人或每段伤害重新播放 `explosion_release`。脱力结束时机由玩法决定。浏览器“完整演示”的三次脉冲仅用于验证动作流程，实际游戏的伤害、伤害次数和回合结束由游戏代码控制。动画事件目前只是视觉对齐标记，没有执行伤害逻辑。

## 导入和继续制作

1. 使用 Spine 4.2 编辑器的 **Import Data** 选择 `export/megumin.json`。
2. 保持 `export/` 与 `images/` 的相对目录；JSON 图片路径是 `../images/`。
3. 检查默认皮肤、18 段动作、`right_hand_lock` 与 `left_hand_lock` 两条 IK，再保存为新的 `.spine` 工程。
4. 正式接入时使用相符的 4.2 运行库；在编辑器中再导出 `.skel` 和正式纹理图集。`megumin.spine-json` 是与 JSON 完全一致的 Godot 后缀副本。

以上为官方格式支持的导入路线；由于本机没有编辑器，**本次没有实测编辑器导入和二进制导出**。

## 绘图与骨架

- 母版：`../megumin-concepts-20261009/quartet/idle-02-right-hand.png`。
- 本次使用内置 imagegen 制作 3 张透明源图：站立拆件、表情/倒地姿态、无重复袖口的上臂接头。未使用 CLI/API 绘图备用流程。
- 完整提示词在 `source/standing-parts-prompt.txt`、`source/expressions-down-prompt.txt`、`source/upper-connectors-prompt.txt`；原始 PNG 都保留。
- 构建脚本仅进行无损矩形切片、图集索引、骨架及关键帧生成，不重画像素。
- 站立部分以刚性区域附件为主，手臂由 IK 约束；帽子、头、披风单独控制。
- 坐姿、仰躺、侧躺使用专用整姿绘图。坐姿与仰躺用网格轮廓排除相邻图块残片，原始纹理保持不变。这些网格还没有做身体内部的蒙皮变形。

## 当前质量边界

站立动作、持杖约束、状态返回和死亡停留已可实际检查。当前仍是动作样机，距离可发布素材还有差距：

- 坐倒、仰躺、起身之间用离散附件切换衔接，需补过渡画或进一步拆分倒地骨架。
- 表情替换图有少量脸形/衣领差异，尚未达到逐像素统一。
- 肩肘遮挡、衣裙变形、帽穗和发梢细节需要美术精修；本版没有宣称是完整的软网格蒙皮。
- 尚无真实游戏伤害绑定、音效、爆裂粒子、碰撞/选择边界调整。

## 构建与检查

需要 Node.js、Python 与 Pillow。开发依赖用 `npm ci --ignore-scripts` 安装。

```powershell
py -X utf8 tools/build_spine.py
node tools/validate.mjs
py -X utf8 tools/package_preview.py
```

`export/validation.json` 记录官方 Spine Core 4.2.95 解析和采样结果：18 段动画、953 个时间点，检查数值有效性、右手握点、双手保持、待机固定点、四条循环接缝、死亡附件和单次释放事件。该报告不替代画面检查，也不代表游戏接入通过。

预览随包保留官方运行库原始版权与许可证：`vendor/SPINE-RUNTIME-LICENSE.txt`。
