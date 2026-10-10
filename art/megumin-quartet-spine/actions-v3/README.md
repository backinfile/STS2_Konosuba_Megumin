# 惠惠 · 原图分层 Spine 动作 v3

**视觉审查更新：idle 已获认可，其余动作仍需返工。** [逐帧问题分析](action-audit.html) 包含 40 个时刻、官方姿态参考、已确认问题和修正顺序。下面的运行时检查通过仅代表数值与播放检查，不代表美术验收通过。本轮审查未修改源图或动画导出数据。

这版把 v1 的其他动作重新绑定到此前右手持杖图的造型上，保留同一张脸、帽子、衣服和法杖；倒地与起身也使用同一套分层骨架连续过渡。它是供审阅、调整和后续接入的动作样机。

- [离线交互预览](preview.html)：可直接用浏览器打开；完整演示、单段播放、拖动时间、慢放、骨骼、深色背景和 320 px 模式。
- [九个关键帧](keyframes.html)：全部由实际导出的 Spine 数据渲染。
- [Spine 导入包](megumin-actions-v3-import.zip)：JSON、图集、原始附件图片和此说明。
- [运行时检查结果](export/validation.json)。

## 本次修正

1. 原图可见区域以 UV 网格切分，避免重新画整张脸或全身后发生造型漂移。被手臂、法杖遮挡的帽檐、帽子吊饰和披风用局部补画承接。左手搭杖另有握持附件。
2. 20 根骨骼、13 个槽位、四组双骨 IK；右手随法杖握点，左手吟唱时贴合第二握点。站立时双脚固定。
3. 眨眼只替换眼部；受击、脱力和死亡使用闭眼、平嘴的小范围表情片段，头发、脸形和眼罩保留。
4. 倒地、起身均为骨骼运动，披风使用标准 Spine deform 时间线接地，没有 v1 的整张倒地图突然换帧。
5. 对纹理做了 AI 细密颗粒/摩尔纹清理；运行时图集采用 2 的幂尺寸和三线性 mipmap 缩小过滤，减少 320 px 下细线闪烁。纹理清理会带来少量线条变化，所以不宣称与 idle-v2 逐像素相同。

## 动作与接入含义

文件采用 Spine 4.2.11 数据格式；本地预览与验证使用官方 Spine WebGL/Core 4.2.95。18 个动作片段，另有一个 `setup_pose` 检查片段。

| 动作 | 秒数 | 用途 |
|---|---:|---|
| `idle_loop` | 4.00 | 轻呼吸、局部眨眼，固定脚与法杖 |
| `cast_short` | 0.70 | 普通出牌短手势，回待机 |
| `chant_enter` | 0.70 | 双手持杖进入吟唱 |
| `chant_loop` | 2.00 | 持续吟唱，等待游戏事件 |
| `chant_cancel` | 0.60 | 取消吟唱，返回待机 |
| `chant_ack` | 0.50 | 吟唱中出牌回应，回吟唱 |
| `attack_short` | 0.65 | 普通出招；0.28 秒 `impact` 事件 |
| `explosion_release` | 0.60 | 爆裂释放；0.40 秒唯一 `release` 事件 |
| `explosion_hold` | 0.60 | 多段伤害期间保持，身体不反复出招 |
| `explosion_exit` | 0.50 | 结算结束后卸力 |
| `hit` | 0.40 | 站立受击，回待机 |
| `hit_chant` | 0.40 | 吟唱受击，回吟唱 |
| `relaxed_fall` | 1.05 | 从卸力姿态经坐倒到躺下 |
| `relaxed_loop` | 3.00 | 躺倒微呼吸 |
| `get_up` | 1.30 | 从躺倒经坐姿恢复待机 |
| `dead` | 1.10 | 从站立倒下，最后姿态保持 |
| `dead_from_down` | 0.35 | 已躺倒时死亡，不先起身 |
| `hit_down` | 0.30 | 倒地时的小幅受击 |
| `setup_pose` | 4.00 | 静态绑定检查，不用于玩法 |

`relaxed_fall` 从 `explosion_exit` 的结束姿势开始。直接从 idle 单独播放会跳到该起点；应按预览中的完整队列检查衔接。普通出牌/受击结束应恢复原状态；吟唱不能被通用“播放完回 idle”逻辑取消。伤害结算次数由游戏控制，预览的三次脉冲只是演示。脱力是演出，不自行添加无法行动的回合规则。

## 导入与验证边界

在匹配 4.2 版本的 Spine 编辑器里使用 Import Data 读取 `export/megumin.json` 或同内容的 `megumin.spine-json`，图片目录为 `../images/`。运行时使用 `megumin.json`、`megumin.atlas` 和同目录五张 PNG 图集页。图集里设置了 `MipMapLinearLinear,Linear`；后续打包/引擎导入时也需保留 mipmap。

本机没有可用的 Spine 编辑器，**没有验证原生编辑器导入，也尚未接入 STS2**；未提供原生 `.spine` 或二进制 `.skel` 文件。官方运行时已经成功解析和播放这些数据。

自动检查覆盖 19 段、2,756 个采样时刻、四肢 IK、网格坐标/UV、4 个循环边界、14 处片段衔接、静态源图坐标、披风接地、爆裂事件唯一性和死亡保持。检查数据用于发现绑定/时间线错误，不代替美术审阅。

视觉上仍是侧向剪纸骨骼动画。坐倒/躺倒的腿部透视、肩肘连接和身体接地还可精修；它们不会因为数值检查通过就成为手绘逐帧质量。去摩尔纹已处理源图和缩小采样，实际游戏的纹理导入设置仍需检查。

## 源图与可复现构建

基础母图为 `art/megumin-concepts-20261009/quartet/idle-02-right-hand.png`。本次纹理清理和局部补画均使用内置 imagegen 工具；对应完整提示词保存在 `source/*-prompt.txt`。

| 文件 | 使用方式 |
|---|---|
| `clean-reference.png` | 清理细密纹理后的原图，保留主要可见区域 |
| `body-base.png` | 移除手臂/法杖后的遮挡补画，提供帽檐、吊饰及披风 |
| `blink-source.png` | 仅取闭眼区域 |
| `tired-expression.png` | 仅取闭眼与平嘴区域 |
| `support-grip.png` | 左手搭杖的握持形状 |
| `costume-underpaint.png` | 早期补画尝试，最终运行时未使用 |

工具只做几何切分、权重、时间线与图集装箱；不通过脚本重绘角色。图集装箱把源像素原样复制到有透明边距的 2048 × 2048 PNG；不重采样源画。网格分区记录在 `source/partition.json`，源图 SHA-256 记录在 `export/manifest.json`。

从 `art/megumin-quartet-spine/` 运行：

```powershell
py -m pip install --target .build-deps -r tools/requirements-actions-v3.txt
npm install
npm run build:actions
npm run test:actions
```

构建顺序为 `build_actions_v3.py` → `bake_floor_v3.mjs` → `validate_actions_v3.mjs` → `package_actions_v3.py` → `gallery_actions_v3.py`。接地变形已写入标准 Spine 数据，运行时不依赖 Python 或自定义接地代码。

参考技术资料：[Spine JSON 格式](https://esotericsoftware.com/spine-json-format)、[Spine Import Data](https://esotericsoftware.com/spine-import)。本地其他模组的 Spine 4.2 文件格式与游戏动画触发参考见上级 README；未复制它们的角色美术。
