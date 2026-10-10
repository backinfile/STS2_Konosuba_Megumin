# 惠惠 Spine 动画 v9

v9 保留 v8 的原始画稿、头部/手掌体积校准和 19 个游戏动作，修改运动路径与节奏。

- 经过姿势使用连续切线；动作起止、实际停顿和反转保留减速。
- 握杖手、头、胸口沿连续曲线移动；头部略先行，手与披风稍后跟随。
- 网格辅助骨骼跟随解剖关节重新定位，避免独立插值造成袖口剪切。
- 按新的运动轨迹分别调整躯干、手臂和腿部的换图时刻。

执行 `npm run build:actions:v9` 构建并验证。`export/validation.json`、`verification/continuity.json` 和 `verification/motion-rhythm.json` 分别记录骨架、体积/跳变和停顿回归检查。

源图与 v8 完全相同；`verification/moire.json` 继承已审核的原尺寸 Mi-Ripple 结果，构建时再次核验所有 31 张使用中图片的 SHA-256。没有重新生成或缩放源图。

本版本仍使用分角度附件；连续速度不能消除所有不同画稿间的轮廓差异。Spine Editor 导入尚未人工验证。

## 查看与验证

- [游戏内原速录像](verification/recordings/index.html)：19 个动作、完整动作链和正常战斗。
- [v8 / v9 原速并排对照](verification/recordings/comparison.html)：进入吟唱、脱力、起身、死亡。
- [下载全部录像](verification/recordings/megumin-v9-native-recordings.zip)
- [Spine 离线预览](preview.html) · [导入包](megumin-actions-v9-import.zip)

五个已复现的经过姿势停顿全部修复；起身三个点从邻域峰值的约 3% 提升到 32%–59%。3511 次运行库采样、原有体积/跳变检查、5 个循环和 17 个动作接缝均通过。原生游戏检查 19 个动作的 57 个时刻，正常战斗经 13 次实际出牌/回合操作进入胜利奖励。

完整动作链 21.60 秒，正常战斗 41.83 秒；录像实测采集最低约 29.80 FPS，无声。`comparison.json` 记录 A/B 录像来源、哈希和对齐时间；并排视频只裁切原生录像，没有变速或补帧。所有验证均不替代用户对动作风格和自然度的最终评价。
