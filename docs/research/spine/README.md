# Spine 研究资料与连续性检查

归档日期：2026-10-10。本目录保存原版资源研究、惠惠 v9 的版本化审查，以及对应的轻量证据。检测工具位于 [`tools/spine-smoothness-auditor`](../../../tools/spine-smoothness-auditor/README.md)。

## 阅读入口

1. [原版全量动画与大姿态切换分析](STS2_Spine全量动画与大姿态切换分析.md)：162 个骨架、948 个动画，包含逐动画机制、状态机和方向性 mix 参数。文件约 3 MB；网页预览受限时可下载后在编辑器搜索。
2. [惠惠 v9 问题与原版对照](惠惠v9_Spine问题与原版对照.md)：19 动作的视觉、结构、事件节拍与状态图审查，明确区分已观察症状、源码判断和未验证风险。
3. [检查工具中文说明](../../../tools/spine-smoothness-auditor/README.zh-CN.md)：JSON / `.skel`、循环接缝、真实 AnimationState mix、连续性信号、离散换图和网格提示。
4. [验证范围与局限](../../../tools/spine-smoothness-auditor/VALIDATION.md)及[精简示例](../../../tools/spine-smoothness-auditor/examples/README.md)。

## 固定版本与结论边界

- 原版研究固定在 [Hexpion/Slay-the-spire-2 `64ed626`](https://github.com/Hexpion/Slay-the-spire-2/tree/64ed626b7ec9692bc54536b0123fc3cb580c28da)，不是所有游戏版本的承诺；具体游戏 build 未确认。
- 惠惠审查固定在 [本仓库 `23d31cc`](https://github.com/backinfile/STS2_Konosuba_Megumin/tree/23d31cc4d17c0102f37aba65a650a29868e2556f)，目标为 `actions-v9`。归档前重新 fetch，远端 main 仍指向该提交。本报告始终作为这个版本的基线，不自动把旧发现延伸为后续版本仍存在的问题。
- 原版“全量”是导出数据的静态覆盖，不等于 948 个动画全都人工逐帧观看。惠惠审查使用提交内原生录像和独立重建，没有在本次归档中启动游戏。
- 端点一致、几何平滑或测试通过都不能证明纹理覆盖、轮廓、美术表演、游戏状态图或实际帧率正确；风险信号数量不是缺陷数量或通用审美分数。

## 随仓库保存的证据

- [原版盘点摘要](data/sts2-inventory-summary.json)：骨架、动画、时间轴、关键记录、导出版本及分类计数。
- 惠惠 [结构统计](data/structural-metrics.json)、[端点与运动统计](data/continuity-metrics.json)、[指定时点翻面统计](data/fold-metrics.json)。这些是旧审查算法的派生数据，与新 CLI 的信号定义不同，不能直接逐项比较数量。
- [起身固定比例接触表](figures/contact_sheets/get_up_focus_fixed.png)、[趴下固定比例接触表](figures/contact_sheets/fall_focus_fixed.png)。这些是单动画 CPU 重建，不是新的游戏实机测试。
- 原生录像抽帧：[get_up 第 67 帧](figures/boundaries/get_up_0067.png)、[relaxed_fall 第 42 帧](figures/boundaries/relaxed_fall_0042.png)。源录像与记录在[固定版本的 recordings](https://github.com/backinfile/STS2_Konosuba_Megumin/tree/23d31cc4d17c0102f37aba65a650a29868e2556f/art/megumin-quartet-spine/actions-v9/verification/recordings)，详细时间对应见 v9 报告。

两份长报告保留了原审计归档的证据标识。原版 `analysis/timelines/*.json`、`analysis/json_skeleton_audit.json`、完整清单及重建中间文件属于仓库外的历史完整数据包，**未包含在本次提交，也不是仓库相对链接**。惠惠报告中其余 `video_sheets/`、`boundaries/`、`contact_sheets/` 图名，以及旧 `structural.mjs` / `continuity.mjs` / `folds.mjs`，同样是外部审计归档标识；已纳入的图和统计在上方有实际链接。阅读主要结论无需这些外部文件；逐键复核原版完整统计仍需完整归档或合法取得对应版本资产另行解析。

## 从本仓库运行工具

需要 Node.js 20+。从仓库根执行：

```sh
cd tools/spine-smoothness-auditor
npm ci --ignore-scripts
npm test
npm run demo
node bin/spine-audit.mjs --help
node bin/spine-audit.mjs --input ../../art/megumin-quartet-spine/actions-v9/export/megumin.json --animations idle_loop,chant_loop,get_up,relaxed_fall,hit,explosion_release --loops idle_loop,chant_loop --transition chant_enter:chant_loop --mix 0.2 --out out-megumin
```

输入同名 atlas 自动加载元数据；无需加载 PNG。结果写到忽略的 `out-megumin/`，不覆盖源资产。`qa/run-real-samples.sh` 默认检查本仓库 v9，原版样本需要使用者自行提供合法本地路径。完整 JSON / CSV 可重跑生成，仓库只收可读报告和精简机器摘要。

## 内容与授权

本次只添加研究文档、派生证据与工具，不修改生产美术、状态代码或候选姿势。未新增原版游戏 `.skel`、贴图、反编译源码、全量逐键/逐帧转储、依赖缓存或运行日志。

第三方游戏、角色和素材的权利归各自权利人。公开可读的来源不意味着获得素材再分发权。工具依赖固定的官方 Spine runtime 4.2.120，使用、集成与分发前须阅读 [Spine runtime 许可证](../../../tools/spine-smoothness-auditor/SPINE-RUNTIMES-LICENSE.txt)并确认相应授权；本研究不授予第三方素材或 Spine 授权。
