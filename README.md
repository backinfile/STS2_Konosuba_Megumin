# STS2 · 惠惠角色 Mod

当前包含**玩法设计研究与独立的角色美术／动画原型**。尚未接入 Slay the Spire 2，不是可安装的 Mod，也不代表卡池、数值或游戏接口已经定稿。

## 最新连续动作 v3

- [v3 连续骨骼小样](art/megumin-v3/README.md)：收窄站距、固定头手与骨长、自然 Idle 起止、无全身姿态切换
- [v3 腿部连接修正版预览](art/megumin-v3/preview/megumin_continuous_v3_legfix.mp4)：5.433 秒、30 fps、1440 × 960
- [v3 修正版静态首帧](art/megumin-v3/preview/leg_review/idle_legfix.png)

本轮修复膝盖连接、靴口重复袜子和裙片误带的皮肤，原版 v3 视频保留供比较。

v3 是连续动作审核小样，尚不是六状态终版。视频为 Godot 原生时间轴导出网格的软件光栅预览，未完成引擎图形窗口或 STS2 实机验收；仍可见少量 cutout 接界。

## 动作重做 v2（保留比较）

- [v2 工程与说明](art/megumin-v2/README.md)：六张独立关键姿态、关节次级运动，默认关闭特效
- [v2 无特效预览](art/megumin-v2/preview/megumin_casting_v2.mp4)：4.233 秒、30 fps、1440 × 900
- [版本对比与验证边界](docs/animation-versions.md)

v2 视频是从实际 Godot 动画／网格数据生成的软件光栅预览，**不是 Godot 图形录屏**；图形着色器及 STS2 接入尚未验证。它是供审阅的重做版本，不代表用户最终验收。

## 从这里开始

- [玩法设计导航](design/README.md)：当前方案、历史探索、结构化卡表与原作资料
- [核心设计简明版](design/惠惠核心设计简明版.html)：三个备选核心与构筑示例（下载后用浏览器打开 HTML）
- [v1 美术与动画使用说明](art/megumin/README.md)：Godot 4.6 项目、六个状态、依赖和验证方法
- [v1 原速动作预览](art/megumin/preview/megumin_reel.mp4)：21.13 秒，30 fps，1440 × 900
- [透明站立终稿](art/megumin/assets/runtime/megumin_idle_neutral.png)：1600 × 1760，地面锚点 (760, 1640)
- [仓库结构说明](docs/repository-layout.md)：文件归属、保留规则与后续扩展原则

## 目录

- `design/`：原有 20 个研究文件，目录关系与文件内容原样保留；其中 `docs/` 为结构化卡表、追踪记录与设计页生成脚本，`参考资料/` 为出处和设计方法
- `art/megumin/`：角色美术与 Godot 动画原型的独立项目根；源图、运行资源、预览、工具和测试分别管理
- `art/megumin-v2/`：独立的六关键姿态重做版，保留自己的项目根和导入设置；与 v1 并列比较
- `art/megumin-v3/`：连续 FK/IK 版本，保留自己的源图、原生时间轴、验证和无特效预览
- `docs/`：跨目录导航和工程接入说明；具体美术制作与验证记录随美术项目保存

先完成角色资源与动作验证，再根据实际 STS2 Mod 接口引入游戏工程。不提前建立空的 cards、powers、relics 等目录，也不把 Godot 展示代码误标为已实现的游戏逻辑。

## 内容与权利

这是以《为美好的世界献上祝福！》惠惠为题材的非官方创作／研究项目，与原作及游戏官方无关联。原作角色及相关商标属于各自权利人。资料中的来源、事实与改编判断请分别阅读；仓库公开不等于获得第三方素材的再授权。
