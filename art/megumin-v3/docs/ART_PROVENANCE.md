# v3 素材来源与改动边界

- `megumin_master.png`：逐字节保留 v1 imagegen 母图；头帽、双臂、双手、裙、两腿和靴全部确定性分件裁取
- `megumin_staff_complete.png`：逐字节保留 v1 imagegen 完整杖；固定 0.83 配准。上下半段仅为遮挡层级划分，严格共用同一刚性变换
- `megumin_occlusion_base.png`：逐字节保留 v1 补底作为来源记录；v3 躯干改用下面的新补底
- `megumin_body_occlusion_v3.png`：imagegen 从同母图生成的去双臂胸腹与腋下补底，只取躯干区域，不用其新头、手或腿替换原件
- `megumin_cape_complete_v3.png`：imagegen 从同母图生成的完整独立披风。替代 v1 的被手遮挡部分与复制 UV 布料补底；只做一次性纵向位置配准及轻微布料网格摆动
- 膝盖覆盖片：对应同一条腿、同一母图膝部的圆形确定性裁切。无手绘或生成新解剖尺寸

所有源 PNG 均未重绘、模糊、抹平或修改 alpha。离线光栅器为显示缩小生成 premultiplied-alpha mip 链，不改写母图。

无六张全身姿态混合、无全身 pose crossfade、無素材间头手尺寸配准动画。
