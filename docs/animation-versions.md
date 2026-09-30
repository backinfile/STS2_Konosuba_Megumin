# 动画版本与验证边界

## v1：首版 cutout 动作

目录：`art/megumin/`，保留不变。

- 六状态，站立分件关节和披风网格，脱力／倒地使用专用姿态
- Godot 4.6.3 实际图形录制，21.133 秒、30 fps
- 独立项目功能测试 26/26 通过
- Attack 事件时点为 0.72 秒

## v2：六关键姿态动作重做

目录：`art/megumin-v2/`，与 v1 并列供比较。

- 蓄势 → 抬肘 → 咏唱 → 全身释放 → 收势 → 脱力，六张独立姿态与两张遮挡修补源图
- 默认无特效，连续的关节次级运动配合不透明关键姿态切换
- 完整 Attack 动作 3.50 秒，事件时点改为 **1.55 秒**；旧版 0.72 秒不可沿用
- 交付预览含尾部停留，共 4.233 秒、127 帧、30 fps、1440 × 900
- 视频是实际 Godot AnimationPlayer / Polygon2D 数据的软件光栅结果，不是引擎图形实录
- 原始图片不做模糊归一化；纹理导入配置保留 mipmap，离线预览使用预乘透明度 mip 和三线性采样

## 仓库整合验证（2026-09-30）

从冻结交付包复制到 `art/megumin-v2/`，保留 `res://` 项目根；重新导入后运行：

```sh
bash art/megumin-v2/tools/run_tests.sh
```

移位重导入后的测试结果为 **65 通过、0 失败**。该测试覆盖六姿态、固定脚锚点、共享法杖与握点、时间轴状态、重复 seek、被打断、死亡／重置及单次事件回调。详情见项目的 `tests/results.json` 与 `tests/godot_test.log`。

未提交 `.godot/`、预览帧缓存、软件导出的中间二进制、AVI、旧四姿态中间视频或重复 ZIP。保留 `.png.import` 中的制作参数；本仓库 manifest 对实际文件重算。

## 尚未验证

- v2 真正 Godot 图形合成、GPU shader 编译和引擎录屏
- STS2 工程集成、角色朝向／缩放／场景背景下的最终效果
- 尚有快速换姿态感与少量道具边缘残留，需要继续美术审阅；自动测试通过不等于用户验收

引擎原生预览需可用图形会话；软件预览重建使用 `render_software_preview.sh`，需要 Godot、Python（NumPy、Pillow）和 ffmpeg。旧 `tools_build.py` 仅保留用于早期几何来源追溯，不应覆盖 v2 时间轴。

## v3：连续 FK/IK 小样

目录：`art/megumin-v3/`。v1/v2 保留不改。

- 固定同一头帽、手、肢体和法杖，刚性分件运行缩放为 1；脚底固定，髋位移由双段腿 IK 求解
- 足底横距从 553px 收窄至 453px，起止为约 8° 松膝的自然 Idle
- 一条连续 5.4 秒原生时间轴；预览包含 0 至 5.4 秒的 163 帧，总时长 5.433 秒，30fps、1440×960
- 没有全身姿态切换或 alpha 交叉淡入，48 项约束与 8 处亚帧边界连续性检查通过
- 仓库副本修正了重建／源图校验所需 v1 相对路径，并重新运行 `bash art/megumin-v3/tools/run_tests.sh`
- 输出仍是 Godot 导出网格的软件光栅预览；未声称引擎图形渲染、最终用户美术验收或 STS2 接入完成
- 这是单动作连续小样，尚无六状态 API、完整倒地、口型或头部换向；右宽袖和高倍膝盖纹理仍可见 cutout 接界

### v3 腿部连接修正版

- 新预览 `art/megumin-v3/preview/megumin_continuous_v3_legfix.mp4`，旧片仍保留
- 膝盖改为连续 UV 网格连接，清除靴口重复袜子和裙片误带皮肤；骨长、头手尺寸、足底锚点和既有时间轴保持
- 自包含 `assets/baseline/` 取代上一版兄弟 v1 目录依赖；仓库副本运行重建与回归验证
- 59 项约束／回归与 8 处阶段边界通过；细节见 `tests/continuous_validation.json`、`tests/timeline_continuity.json` 和 `docs/LEG_CONNECTION_REVIEW.md`
- 仍为软件光栅预览，不是 Godot 图形实录或 STS2 验收；少量 cutout 风格及高倍纹理弯曲仍保留说明

## v6：侧身造型与稳站主链阶段存档

- 当前文件 `art/megumin-v6/preview/megumin_v6_mage_legmotion_fix.mp4`：7.233秒、217帧、30fps、1440×960
- 已确认的侧身造型，修正腿部外蹲／站姿，主链资产及轨道对应该预览
- 快照保存录制后新增的默认关闭实验项 heel_raise/cape_collapse；不宣称全部源码与视频录制时逐字节相同
- Idle/Cast/Attack/Hit/Relaxed 独立轨道进行中，尚未完整状态视频及目视验收；Dead_unreviewed_legacy.tres 和 dead_probe 为未验草案
- 主链41项数值检查、10处边界连续性与headless预览smoke复验；不代表六状态完成
- 软件光栅预览不是Godot图形后端／STS2游戏实机验收；具体阶段边界见项目README
- 此提交保留先前已提交版本，不引入商用游戏文件、缓存或凭据

### v6 后续五状态交付

当前主片 `art/megumin-v6/preview/megumin_v6_five_states_review.mp4`，19.366667秒／581帧／30fps。Idle、Cast、Attack、Hit、Relaxed 已拆分为独立可调用状态，Dead 未加载、请求返回 false，不把实验资源冒充成品。

制作方隔离重建验证了38份资源及822份原生导出字节一致；仓库副本重新运行41项主链、120项五状态纯数值与44项运行时检查，并对MP4完整解码；另复跑构建，18份本地几何/图像/动画资源哈希不变。制作方123项完整检查包含渲染项，仓库本次未重新渲染全部帧。构建与运行不依赖其他版本。旧状态存档可从提交 `264ff53114cba6c1c372a9782315044398811181` 找回。

数值与静帧检查不等于完整原速视频目视验收，Dead 与STS2实机接入仍未完成。
