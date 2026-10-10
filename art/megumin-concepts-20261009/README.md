# 惠惠立绘候选 · 2026-10-09

依据用户要求查找官方参考后，使用内置 image_gen 重绘三张候选。当前仅供选择，未获选为新母版，未替换 v6 资源。

| 候选 | 文件 | 方向 |
| --- | --- | --- |
| A | A-anime-model.png | 克制、略带得意的动画设定感，自然持杖站姿 |
| B | B-bakuen-lively.png | 活泼表情、扶帽动作，参考《爆焰》的角色视觉图 |
| C | C-battle-ready.png | 朝右准备施法，更适合战斗展示的轮廓 |
| C2 | C2-facing-right.png | 根据用户追加建议，让肩胸、腰胯及双脚进一步统一朝右的三分之四视角 |
| A2 | A2-facing-right.png | A 的整体右转版，保留安静得意的表情及自然垂臂站姿 |
| B2 | B2-facing-right.png | B 的整体右转版，保留活泼笑容及扶帽动作 |
| A3 | A3-relaxed-idle.png | 延续 A2，缩短腿部观感、放松肩臂和手指的 idle 基础姿态候选 |

三张均为 AI 辅助同人重绘，不是官方原画。官方素材仅作为参考保存在 references/，未接入游戏或重新发布。

## 官方来源

检索及下载日期：2026-10-09。

- [第一季角色设定页](https://konosuba.com/1st/character/)：[设定图](https://konosuba.com/1st/character/img/megumin.png)。用于正侧面脸型、头身比例、帽子与服装构造。
- [《为美好的世界献上爆焰！》角色页](https://konosuba.com/bakuen/character/)：[冒险者服立绘](https://konosuba.com/bakuen/character/img/megmin-2.png)。用于表情、线条、持杖手与服装配色。此参考图宝珠为蓝色；本轮候选为保持模组方向统一，特意设定为红色。
- [第三季角色页](https://konosuba.com/3rd/character/)：[惠惠立绘](https://konosuba.com/3rd/character/img/megumin.png)。用于核对服装及帽子结构；其站姿和第一季设定图重复，不当作独立动作参考。

## 制作记录

- 三张分别调用内置 image_gen 生成，使用真实透明背景。
- A 初稿出现双帽穗，已用内置 image_gen 定向修正为单帽尖、单帽穗；该错误初稿不列入候选。
- 完整实际提示词见 prompts.json，包括 A 的修正提示词。
- 尚未做角色分件、骨架、动画或游戏内缩放验收。此阶段先选择造型和神态。
- C2 使用内置 image_gen 编辑 C，完整提示词见 C2-facing-right-prompt.json；是朝向对照稿，尚未作为最终母版选定。
- A2、B2 分别使用内置 image_gen 编辑 A、B，提示词见 right-facing-prompts.json；和现有 C2 一起用于朝右造型选择。
- A3 合并用户关于舒适 idle 站姿和腿偏长的反馈，使用内置 image_gen 编辑 A2，参考第一季官方设定图；提示词见 A3-relaxed-idle-prompt.json。尚未获最终姿态或比例验收。

## 从零重画

用户随后要求停止基于当前图片修改，重新生成。以下两张分别使用内置 image_gen 文生图，未传入旧图作为图片参考或编辑底图。官方参考经目视后转写为提示词中的造型描述。

- `from-scratch/01-idle.png`：自然持杖 idle、帽尖向后垂的新起点；用户反馈腿显短。
- `from-scratch/02-idle-balanced.png`：再次从零生成，将自然腰线、较短裙身及适度修长的腿部一起校正；保留放松站姿和向后帽尖，等待用户确认。
- 完整提示词：`from-scratch/prompts.json`。未替换游戏或动画工程中的资源。
