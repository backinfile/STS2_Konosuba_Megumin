# 验证记录与示例解读

验证日期：2026-10-10。环境：Node.js 24.19.0；官方 Spine runtime 4.2.120。包声明 Node >=20；没有声称实际测试过所有 Node 20+ 次版本。

## 自动测试

`npm test`：45/45 通过（12 个集成/接口测试 + 33 个独立对抗测试）。详细用例与方法见 `qa/QA_REPORT.md`。合成夹具都随包提供，无须游戏文件即可执行。

特别回归了一个真实发现的算法误报：低阶 loop 端点差分曾把匀速 720°/s 整圈旋转判为速度接缝，改为高阶端点估计加显式误差提示后，在 30、60、120 FPS 下均通过；真实速度反向接缝仍被识别。误差提示是数值诊断启发式，不是视觉质量保证。

## 真实素材兼容/输出检查

全部使用真实官方 runtime，60 FPS、physics=none、匹配 atlas；未重新导出或修改输入。

- Megumin v9 JSON：idle_loop、chant_loop、get_up、relaxed_fall、hit、explosion_release，以及 chant_enter → chant_loop 的 0.2 s mix；另一个独立回归单独检查了 chant_enter。
- Silent `.skel`：idle_loop、attack，以及 attack → idle_loop 的 0.2 s mix。
- Ironclad `.skel`：idle_loop、attack，以及 attack → idle_loop 的 0.2 s mix。
- Lagavulin Matriarch `.skel`：idle_loop、wake_up、零时长 `_tracks/eyes_closed_loop`，以及 wake_up → idle_loop 的 0.2 s mix。

Megumin 和 Silent 的可读报告与精简机器摘要在 [`examples/`](examples/README.md)，完整逐帧 JSON / CSV 未随仓库提交，可按说明重跑；Ironclad/Lagavulin 和额外 Megumin 回归的紧凑摘要在 `qa/real-sample-summary.json`。输入 SHA-256、具体 Spine 版本、归一化标尺、阈值和 runtime 版本都已记录。游戏素材不随包分发。

## Megumin：已知画面问题与脚本信号分开看

人工逐帧审查已知：

- get_up 约 0.95–1.05 s：衣服/躯干的覆盖或附件匹配问题，可能露出背景。单靠骨骼速度或三角形面积无法证明洞的来源。
- relaxed_fall 约 0.70–0.80 s：披风刺状折叠；三角形翻面可提供部分佐证，但不是所有异常像素的解释。
- get_up 约 1.60 s：腿部投影突变需目测确认。

脚本的实际结果：

- idle_loop 和 chant_loop 的端点位置差均为 0；端点速度差约 0.0000132 与 0.0000134 个参考长度/秒，均无当前阈值的循环速度风险。
- get_up：17 条连续性信号，全部来自可见几何，主要集中在约 3.2 s 的法杖运动；另有 97 条离散事件、162 条三角形提示。**这些结果没有自动定位或解释 0.95–1.05 s 的背景洞。**
- relaxed_fall：0 条默认阈值的连续性信号、36 条离散事件、91 条三角形提示。其中 0.7167/0.7333 s 披风有翻面提示、0.7667 s 有退化提示。**0 条连续性信号并不意味着这段没有明显画面问题。**
- chant_enter → chant_loop 的 0.2 s mix：当前设置下无连续性尖峰；不等于任何游戏控制器/轨道组合都已验证。

三角形提示包括初始就很薄或退化的几何、透视和有意镜像，因此数目也不能当“坏三角形”总数。

## 原版对照为什么不能用于机械打分

Silent idle_loop 的 33 条连续性信号全部属于骨骼探针，可见几何为 0；最强 loop 速度差来自不直接影响可见附件的 blade_shine 辅助骨，且数值误差提示更大，因此没有判定速度风险。它说明隐藏/辅助骨过滤的重要性。

原版攻击动画常有强冲击、附件切换和辅助轨道变化：当前默认设置下，Silent attack 产生 11,982 条点×时间×指标信号，Ironclad attack 为 5,509 条。它们**不是缺陷数量，也不表明它们比 Megumin 差**。要判断表现是否自然，必须结合设计意图、可见几何、实际控制器和逐帧画面。

这批对照只验证输入可解析、计算可复现、输出能解释，不代表以这些样本拟合过阈值或审美评分模型。

## 干净安装与执行

已在单独空目录，用固定 package-lock 从 npm 官方仓库执行 `npm ci --ignore-scripts --no-audit --no-fund`，实际新装 1 个包；未依赖工程里的 node_modules 符号链接。缓存可通过 npm 的 `--cache` 参数指定到本机可写目录。

干净目录的完整测试与 `npm run demo` 在原工具交付前再次执行。迁入仓库后的复核见下节；临时测试日志、交付包校验文件及 node_modules 不纳入版本控制。

## 复现

```bash
npm ci --ignore-scripts
npm test
npm run demo
node bin/spine-audit.mjs --input /your/megumin.json --animations idle_loop,chant_loop,get_up,relaxed_fall,hit,explosion_release --loops idle_loop,chant_loop --transition chant_enter:chant_loop --mix 0.2 --out out-megumin
node bin/spine-audit.mjs --input /your/silent.skel --animations idle_loop,attack --loops idle_loop --transition attack:idle_loop --mix 0.2 --out out-silent
```

其他本地真实素材回归可通过 `qa/run-real-samples.sh` 的环境变量指定你自己的素材路径；它不是 `npm test` 的必要条件。

## 迁入仓库后的复核

2026-10-10，基于仓库 main `23d31cc4d17c0102f37aba65a650a29868e2556f` 的独立干净工作树，使用 Node.js v24.19.0：

- 在迁入后的工具目录重新执行 `npm ci --ignore-scripts --no-audit --no-fund`，安装固定依赖 1 个。
- `npm test`：45/45 通过，0 失败、0 跳过。
- `npm run demo`、CLI `--help`、`bash -n qa/run-real-samples.sh` 全部成功。
- `bash qa/run-real-samples.sh`：使用仓库相对路径再次读取 v9 JSON 及匹配 atlas，完成 idle_loop、chant_enter、chant_loop 与 0.2 秒 mix 检查。两个循环的位置差均为 0，速度差约 0.0000132 / 0.0000134；chant_enter 为 18 条连续性信号，mix 为 0 条。
- 未提供原版本地路径，因此这次迁入复核明确跳过 Ironclad / Lagavulin；上文原版检查属于工具交付前记录。
- 本次没有执行 Mod 构建、Godot / STS2 游戏启动或新的游戏实机测试。
