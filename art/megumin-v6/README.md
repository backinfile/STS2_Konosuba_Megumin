# 惠惠v6 当前阶段保存

用户要求保存当前状态。此为稳站修正主链与进行中状态工作的独立快照，不是六状态终版。

先看 `preview/megumin_v6_mage_legmotion_fix.mp4`，7.233秒、217帧、30fps、1440×960，原速无特效。主链骨架/纹理/动作与此片匹配；录制后代码新增默认关闭的实验 heel_raise/cape_collapse，不能称源码字节级相同。

- MageCast主链：已渲染、41项及10边界检查通过，采样关键帧视觉检查通过；视频来自Godot真实时间轴数据的离线软件光栅
- Idle/Cast/Attack/Hit/Relaxed：独立轨道已接入并数值采样，尚未完整状态视频与目视验收
- Dead：仅实验候选，`Dead_unreviewed_legacy.tres`明确未完成、不当作可用Dead；`preview/dead_probe`也是未验候选
- 尚未做STS2游戏内/图形后端验证。旧主链阶段片保留作问题对照，不当最新版本

## 运行与复验
Godot4.6.x打开project.godot即可运行已有场景。工具依赖Python、NumPy、SciPy、Pillow，视频编码另需ffmpeg。

`bash tools/run_tests.sh`会导入、真实时间轴导出、主链数值检查、连续性检查和headless场景smoke。构建工具为tools/build_v6.py与tools/build_timeline.py；状态脚本build_states_v6.py仍在开发中。

未打包Godot缓存、重复逐帧软件输出、Python缓存、import元数据和日志；源图、注册几何、动作、脚本、测试JSON、文档与关键对照/两阶段MP4均保留。
