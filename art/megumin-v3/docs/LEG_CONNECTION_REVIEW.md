# v3 腿部连接修正版（冻结交付）

## 结论

没有把腿骨加长，也没有为回应“腿是不是长了”的猜测直接缩腿。确认并修复了三处连接问题：

1. 大腿、胫骨硬切后贴圆形膝盖，带来粗细和纹理方向跳变
2. 靴粗裁夹带原袜子，固定靴与转动胫骨形成重复水平断口或尖楔
3. 裙粗裁包含真实前裙边以下约20–45px的裸露大腿，固定裙层和活动腿发生错位

## 比例诊断

以完全相同的头部大小和位置对齐母图：腰的高度差约0；左膝高1.76px，右膝低5.75px；足底低14.28px。骨段长度保持不变，但收窄站距和近直立姿势使髋到足底的垂直投影增加：左约4.0%，右约1.1%。因此可以解释部分“更长”的观感，不应把固定骨长说成屏幕投影完全不变。

- 同头比例图：`preview/leg_review/source_vs_delivered_same_head.png`
- 数据：`preview/leg_review/source_proportion_measurements.json`

## 本轮变更

- 每条腿改为单一同源UV网格，移除圆形膝盖盖片
- 膝周±44px窄带平滑混合两骨旋转，保持各顶点到膝中心的半径；窄带外的大腿/胫骨维持刚性
- 裙下髋连接使用左70px、右90px的局部旋转过渡。这是经逐帧无翻面验证的安全带；较短52px测试出现少量翻面，已弃用
- 前裙沿真实布边精裁，后裙摆移到腿后层；裁掉裙和靴误带的皮肤/袜子
- 无新生成素材，无源PNG/alpha修改，无腿骨缩放，无动作轨道/骨锚/站距修改

## 可看文件

- 新片：`preview/megumin_continuous_v3_legfix.mp4`，1440×960，30fps，163帧，5.433333秒
- 新片 SHA256：`5a7fc25713e5a47fa420d1ac7830b72998fb6f985f8946baac0b5cce8c67c99c`
- 旧冻结片：`preview/megumin_continuous_v3.mp4`，SHA256 仍为 `f7ba49caf1db3b2fe3479c3ff9c1afae1f8a3a0cdbc1f3747b7a210d2bf8d705`
- 对照近景：`preview/leg_review/idle_legs_before_after.png`、`release_legs_before_after.png`、`settle_legs_before_after.png`
- 新全图静帧：`preview/leg_review/idle_legfix.png`、`release_legfix.png`、`end_legfix.png`

## 验证

- `tests/legfix_validation.json`：59/59通过
- 全163帧两腿有效三角形翻面为0；最小三角面积比例：左0.276，右0.199
- 完整母图腿轮廓网格覆盖比例约1.0
- 远离关节带的骨段刚性误差小于0.00013px；髋/膝半径误差小于0.00008px
- 冻结版已有骨位置、旋转逐帧最大差为0；原Animation资源逐字节一致
- 足底/靴锚零漂移，头手臂/完整杖尺寸不变
- 原8处阶段边界连续性验证通过；起止仍为左右膝约8°的自然站姿

本轮仍为Godot真实时间轴/网格导出后的离线软件光栅预览，不是Godot图形后端实录。本目录已冻结为独立 legfix 交付包，旧包与旧视频保留。Site 与仓库同步由交付流程单独完成。旧工程的 bf0e567 快照已另行保留。

## 独立包复验

解压后在工程根目录运行 `bash tools/run_tests.sh`；需要 Godot 4.6.x、Python、NumPy、SciPy、Pillow。重新构建可先运行 `python tools/build_continuous.py`。此过程不需要显示服务器，也不会录制图形窗口。
