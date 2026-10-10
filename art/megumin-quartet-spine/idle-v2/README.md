# 惠惠 Idle v2：原图蒙皮修正

这版修复旧样机从原图到动画发生的形状与摆位偏移。以此前的 `idle-02-right-hand.png` 为唯一可见美术，PNG 按字节原样复制；没有重新生成头、衣服、四肢或法杖。

## 查看与导入

- `preview.html`：可离线打开；对照旧版、修正版和原图，支持叠加、拖帧、320 px 和网格显示。
- `megumin-idle-v2-import.zip`：Spine 4.2 JSON、图集和原图。
- 编辑器 Import Data 选择 `export/megumin-idle.json`，保留同级 `images/`；图片路径为 `../images/`。
- `megumin-idle.spine-json` 是相同数据的 Godot 后缀副本。

本机没有 Spine 编辑器，尚未实测编辑器导入、二进制导出或 STS2 接入。数据已经由官方 Spine Core / WebGL 4.2.95 实际解析和播放。

## 修复内容

原图的宽帽檐、脸形与发束、肩颈层次、斜腰带与下摆、右袖和握手体积、垂过下摆的左手、倾斜绷带腿和法杖比例均直接保留。

14 根骨骼控制一张连续加权网格（2,891 顶点、5,568 三角形）。每个顶点由原图像素坐标计算绑定位置，局部权重控制胸口、头、帽子、发梢、手臂与披风的细微运动。脚、握手与法杖区域锁定。连续网格在当前小幅运动下不产生拆件缝隙；没有新增遮挡后内容。

- `idle_loop`：4 秒轻呼吸，首尾闭合。在角色高 320 px 时，最大网格位移约 0.62 px。
- `setup_pose`：4 秒静态原姿，用于编辑器和原图对照。
- 不切换表情，不用重画整张脸来做眨眼。

## 验证与范围

`export/validation.json`：241 个时间点的官方运行库验证。静态坐标最大误差低于 0.00003 px（320 px 身高下）；循环首尾误差为零；杖尖、红珠、主握手、杖底和双脚落点漂移为零；无三角形翻转。

预览页面还会实际用 WebGL 对比静态网格与普通原图附件，显示逐通道像素误差。PNG 的 SHA-256 在 `export/manifest.json` 中记录，导出纹理与原图完全一致。

**这次只重建 idle。** 这是一张连续网格，不能据此宣称已经完成可大幅抬手、转身、吟唱或倒地的分层角色。那些动作需要按原图重新拆层并补遮挡画，再重新绑定。旧版 18 段动作仍保存在上一级目录，作为流程样机，不会在这个修正版里混播。

重建命令（项目根目录）：

```powershell
py -X utf8 art/megumin-quartet-spine/tools/build_idle_v2.py
node art/megumin-quartet-spine/tools/validate_idle_v2.mjs
py -X utf8 art/megumin-quartet-spine/tools/package_idle_v2.py
```

图像处理范围：构建脚本只复制原 PNG；没有绘图、裁剪、重采样或修图。原图来自此前内置 imagegen 的右手持杖修正稿。
