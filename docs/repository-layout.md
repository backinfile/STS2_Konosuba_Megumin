# 仓库结构与维护约定

## 研究资料

`design/` 的研究资料最初从提交 `c270c0e7d1486128bd41748ef968f419175359ae` 整体迁入。2026-10-08按用户要求删除更早的方案文件，仅保留当前魔力积蓄方案和暂存的爆裂狂方案；原作与设计方法资料继续保留。`README.md` 是当前设计导航，旧文件数量和原样保留约定不再约束用户明确要求的清理。

`design/暂存/` 保存可读的方案快照，`design/docs/暂存/` 保存对应结构化数据。暂存不是Git暂存区，也不表示当前推荐方案。

设计页生成命令仍为：

```sh
python design/docs/build_simple_design.py
```

脚本以自身位置定位 `design/`，不依赖启动目录。历史参考资料本来就提到的外部工作区文件并未因此加入本仓库。

## 美术与动画

美术原型放在 `art/megumin/`，该目录作为 Godot 的项目根。完整保留项目内部 `res://` 路径，不能单独把 scenes、animations 或 scripts 移到仓库根。

职责分工：

- `assets/source/`：母图、补底与独立道具等制作源素材
- `assets/poses/`：特定姿势图
- `assets/runtime/`：动画运行用的纹理资源；仅表示原型用途，未保证符合 STS2 最终导入规格
- `animations/`、`scenes/`、`scripts/`：Godot 动作资源、场景和展示控制
- `preview/`：正常播放速度的视频与精选关键帧
- 制作脚本：与资源项目同级存放，依赖及重建命令由项目 README 说明
- `tests/`、项目文档：资源检查、烟测、人工复核结果以及未验证项

源图与导出结果都保留，不将生成缓存当作源文件。排除 `.godot/`、Python 缓存、临时录制 AVI、临时日志与凭据；预览 MP4 可以纳入版本控制。

## 游戏接入与测试

`mod/` 是已在游戏 0.107.1 与 BaseLib 3.4.7 中验证的 C# 角色工程。`tools/` 保存项目启动器、构建与回归脚本，MCP 桥接源码位于 `tools/vendor/STS2_Mcp/`，附来源记录和 MIT 许可证。构建默认复制 `art/megumin-quartet-spine/actions-v9/export/` 到 Mod 的 `animation/`，将 JSON 使用 `.spine-json` 后缀以匹配游戏原生加载器；`-Actions` 参数可选择历史版本。

`.local/` 中的游戏硬链接、独立存档、工具环境与日志不提交；`dist/` 为构建结果。游戏本体和 BaseLib 由本机安装提供，不放入 Mod 分发包。操作方法见 [项目内测试说明](mod-lab.md)。

不要将设计卡表的候选规则、动画播放回调或视觉特效描述成已实现的游戏伤害、状态、卡牌或正式 API。

## 动画版本并存

- `art/megumin/` 保留冻结 v1，路径与源内容不改
- `art/megumin-v2/` 是独立可打开的动作重做项目；不直接覆盖 v1，因此原预览和事件时点仍可对照
- 两个项目各自保有 `res://` 根，避免跨项目资源路径依赖；相同源素材由 Git blob 去重保存，不把 ZIP 或旧录制中间件再次加入
- v2 的 `.png.import` 包含已设置的 mipmap 导入参数，属于应保留的纹理配置；`.godot/` 才是应排除的实际导入缓存

- `art/megumin-v3/` 保留连续骨骼小样，v1/v2 不覆盖。腿部连接修正版将基线几何与原图哈希收进 `assets/baseline/`，重建、验证与 Godot 运行均不依赖兄弟 v1 目录。只提交最终预览与结构化检查报告，不提交原生几何帧转储、逐帧中间图或临时日志。

- `art/megumin-v6/` 是用户要求立即保存的制作中快照；未等六状态完成。已复核主链与尚未完成的独立状态在项目 README 区分，候选 Dead 明确保留未验名称。快照与活动制作源分离，后续改动另行提交。

- v6 后续五状态交付在原目录更新。前一阶段保存于 Git 历史 `264ff53114cba6c1c372a9782315044398811181`；移除旧错误阶段片、Dead probe 与被取代的阶段 manifest，以当前五状态 README/MANIFEST 为准。

- `art/megumin-quartet-spine/actions-v7/` 保留尺寸跳变复现基线；`actions-v8/` 保留校准版；`actions-v9/` 为当前连续节奏版本。`verification/` 保存连续性、去摩尔纹、原生游戏检查与 v8/v9 原速录像对照，数据通过不能替代动作画面验收。

## Spine 研究与诊断

`docs/research/spine/` 保存固定版本的原版研究、惠惠 v9 审查、少量派生统计和重点图证。`tools/spine-smoothness-auditor/` 为独立 Node.js 诊断工具，固定官方 Spine runtime 依赖并附授权说明。全量审计包、原版游戏资产、node_modules、逐帧运行输出及临时日志不提交。资料归档不代表修改动画资产或完成新一轮游戏实机验证。
