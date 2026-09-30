# 首版整合验证（2026-09-30）

## 已验证

- 初始提交的 20 个研究文件迁入 `design/` 后逐字节一致，内部目录关系不变
- `python design/docs/build_simple_design.py` 可运行，重新生成的简明版 HTML 与初始版本逐字节一致
- 美术源自已验收的 v1 包；在 `art/megumin/` 路径重新导入并执行 `tests/test_rig.gd`：26 通过、0 失败
- 验证引擎 Godot 4.6.3；既有视频为实际渲染的六状态原速输出，1440 × 900、30 fps、634 帧、21.133 秒
- 提交不包含 `.godot/`、`.import`、AVI、重复 ZIP 或临时录制日志；功能测试日志保留

仓库副本首次运行时，环境已有的 XDG 目录不可写，导致 Godot 缓存与配置初始化失败；显式指定可写位置后重跑通过。受限环境可这样运行（路径可自行改为可写位置）：

```sh
XDG_CACHE_HOME=/tmp/megumin-test/cache \
XDG_CONFIG_HOME=/tmp/megumin-test/config \
XDG_DATA_HOME=/tmp/megumin-test/data \
  bash art/megumin/tools/run_tests.sh
```

`art/megumin/MANIFEST.json` 按本仓库实际提交文件重算；独立交付 ZIP 的原始清单保持不变。本仓库删除了两份临时视频导出日志，保留了测试证据。

## 尚未验证／已知边界

- 没有 STS2 工程、游戏加载、API、卡牌结算或战斗集成测试
- Cast 是有限时长演示，不是跨回合持续预备；光束是演示 VFX，信号不是游戏伤害结算
- Relaxed / Dead 使用专用姿态图过渡，未模拟完整的骨骼跪倒运动；高倍仍可能看到 UV 拼接边缘
- 逻辑测试不等于全帧美术验收；首版常态尺寸已目视复核，后续仍需在实际游戏背景、缩放与角色朝向下复核
- 重新录制视频需要本地图形会话和 ffmpeg；纯 headless 只用于逻辑验证
