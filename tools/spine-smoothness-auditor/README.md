# Spine Smoothness Auditor

Spine 4.2 动画连续性风险检查 CLI。支持 JSON / `.skel`、世界骨骼与可见网格、速度/加速度/jerk、循环接缝、AnimationState mix、附件/层序事件与网格翻面提示。

完整中文说明：[README.zh-CN.md](README.zh-CN.md)

验证范围与已知局限：[VALIDATION.md](VALIDATION.md)

```bash
npm ci --ignore-scripts
npm test
npm run demo
node bin/spine-audit.mjs --help
```

输出诊断信号，不提供未经校准的通用审美分数。不包含原始游戏素材。请遵守 [Spine runtime 授权](SPINE-RUNTIMES-LICENSE.txt)。
