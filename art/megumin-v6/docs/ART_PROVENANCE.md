# v6 美术来源与注册边界

唯一已批准造型为 `assets/source/megumin_approved_v6.png`（由用户认可v5官方参考稿再向右转身）；`megumin_master_v6.png`如存在是工程使用副本。官方参考出处保存在前阶段 `megumin-official-base-review-v5/OFFICIAL_SOURCES.txt`，本工程不会将新补图中的头脸或手当成替代批准稿。

以下补图均由内置imagegen仅引用批准v6生成，保存raw原件：

- `megumin_backing_v6_raw.png`：去双臂、腿、法杖并补胸侧/肩根和披风。生成发生构图漂移，必须胸系带/腰带配准后只取缺失遮挡区
- `megumin_cape_v6_raw.png`：独立完整披风，补人物遮挡区域。一次性注册到原肩/边缘，不能以生成外框放大角色
- `megumin_staff_v6_raw.png`：完整杖，补握手遮挡。原端点/珠心为尺度依据，不能把生成长度漂移带入动画
- `megumin_unstaffed_v6_raw.png`：只去杖人物，用于白绷带腿被杖遮挡的窄条修复，不替换头脸/手
- `megumin_free_arm_v6_raw.png`：完整自由左臂红袖，补躯干遮住的上臂。生成位置与大小漂移，肩肘腕需一次注册到原批准稿；原手从母图取

配准后固定的分件尺寸才是动画基准；逐帧缩放四肢弥补动作是不允许的。髋/踝等被衣物遮住处为解剖估计，分别在裙内和靴内。骨段测试用于验证时序不变量，不代替人体造型视觉验收。

透明PNG保存原alpha。原尺寸布料去摩尔纹检查见MOIRE_BASE_CHECK.txt；未见伪影则保留像素，不为“去AI感”抹平轮廓。
