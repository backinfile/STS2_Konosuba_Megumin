# 项目内 Mod 与测试环境

开发测试版：游戏 0.107.1、BaseLib 3.4.7、.NET SDK 9、Windows。可选角色为「惠惠（测试）」，独立角色 ID 为 `MEGUMINMOD-MEGUMIN`。

## 一键启动

在仓库根目录的 PowerShell 中执行：

```powershell
./tools/prepare-lab.ps1
./tools/build-mod.ps1
./tools/start-lab.ps1 -Visible
```

准备脚本默认读取本机 Steam 游戏与 Workshop 的 BaseLib 路径；可用 `-GameDir`、`-BaseLibDir` 指定自己的位置。MCP 源码已保存在 `tools/vendor/STS2_Mcp/`，包含 MIT 许可证和来源记录；无需其他项目目录。只有需要重新导入桥接源码时才传 `-McpSource`。

`start-lab.ps1` 默认后台启动、静音且不抢焦点；加 `-Visible` 才显示窗口。`-Build` 会先重新构建。`-Headless` 用于逻辑检查，不能用于画面验收。关闭测试游戏：

```powershell
./tools/stop-lab.ps1
```

测试游戏在 `.local/game/`；只为游戏只读运行文件建立硬链接，mod、配置和日志独立。存档位于 `.local/userdata/`，通过 `%APPDATA%/MeguminModLab-STS2_Konosuba_Megumin` 联接访问。启动时关闭 Steam 接口，使用独立测试档案。准备和关闭脚本均不会操作正常 Steam 游戏进程。

## Mod 输出

`dist/MeguminMod/` 是可安装 mod 目录，包含 DLL、清单、Spine JSON、图集和 PNG。压缩包为 `dist/MeguminMod-0.1.0-dev.zip`。在其他游戏安装中使用时，将 `MeguminMod` 文件夹放进 `mods/`，并安装兼容 BaseLib。

角色战斗画面使用游戏原生 SpineSprite，19 个动画已可调用。生命 70、能量 3、金币 99；初始牌组、卡池、遗物池、药水池来自原版战士，起始遗物为燃烧之血。选择头像等资源仍是 BaseLib 占位图。正式卡牌和爆裂机制不在这个测试版中。

测试专用 HTTP 服务仅在项目启动器设置 `MEGUMIN_LAB=1` 时启用，普通安装不会开启该服务。

## 自动化接口

- `http://127.0.0.1:15528`：游戏控制桥，支持菜单、地图、出牌、奖励、截图和录制。
- `http://127.0.0.1:15529/health`：角色、存档目录与原生 Spine 就绪状态。
- `POST /animation`：例如 `{"name":"chant_enter","time":0.48333}`，按时间定位并冻结；去掉 `time` 可播放，`loop:true` 循环。
- `POST /render`：`{}`，在最小化窗口中主动刷新用于截图的游戏视口。
- `POST /quit`：`{}`，关闭当前测试游戏。

MCP stdio 启动入口为 `./tools/start-mcp.ps1`，使用 `.local/mcp-env/` 虚拟环境，首次启动会安装 `tools/mcp-requirements.txt` 中的依赖。客户端应把这个脚本作为 stdio 服务器启动；它连接端口 15528，不需要配置全局游戏端口。已实测发现 83 个工具，并通过 `get_game_state` 读取角色状态。

## 回归检查

先在独立测试档中进入惠惠战斗，再执行：

```powershell
py tools/test-lab.py --combat
.local/mcp-env/Scripts/python.exe -X utf8 tools/test-mcp.py
py tools/capture_animation_lab.py --clip chant_enter --switches
```

第一条会检查 19 个动作的原生渲染并自动打完当前战斗，因此会推进测试存档。省略 `--combat` 只检查动画。第三条记录指定动作的换图边界。报告和截图保存在 `art/megumin-quartet-spine/actions-v8/verification/`。

## 游戏内原速录像

[录像索引](../art/megumin-quartet-spine/actions-v8/verification/recordings/index.html) 包含 19 个单项动作、完整动作链和正常战斗。视频为游戏视口实时录制，1 倍速、1280×720、30 FPS 编码、无声；单项动作保留前后姿势。动作展示由测试接口触发，正常战斗由实际出牌与回合操作触发。

在惠惠战斗的出牌阶段执行：

```powershell
py -X utf8 tools/record-native-animations.py
py -X utf8 tools/record-native-combat.py
py -X utf8 tools/verify-native-recordings.py
py -X utf8 tools/package-native-recordings.py
```

第二条会推进当前测试战斗。`--only full-sequence` 可只录完整动作链。录像接口在独立测试环境中会逐次刷新最小化游戏的原生视口，避免输出重复旧画面；不修改动画时间或速度。每个视频的 JSON 保留实际采集帧率、重复帧数量及动作时间线，检查脚本验证可见角色与实际画面变化。

## 离线检查

离线几何检查：

```powershell
cd art/megumin-quartet-spine
npm run test:actions:v8
```

图片去摩尔纹检查入口：`.local/moire-env/Scripts/python.exe -X utf8 tools/check-animation-moire.py`，在仓库根目录运行。环境安装 Mi-Ripple 0.1.0，来源及精确提交记录在 `verification/moire.json`。脚本只在独立目录输出候选与诊断；查看热点、裁切和处理对比后记录采用结果。构建会校验当前图片哈希对应已完成的复核，图片变化时必须重新检查。

测试覆盖角色加载、进入战斗、攻击、防御、受击、回合切换、战斗胜利、奖励与重新读档，未验证完整通关、多人游戏或其他 mod 的兼容性。后台测试使用 Compatibility 渲染器，原版部分粒子子发射器会有不支持提示；角色 Spine 画面使用实际游戏图形后端验证。
