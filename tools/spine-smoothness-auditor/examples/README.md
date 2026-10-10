# 精简示例

本目录保留原始检查的 `report.md` 与投影后的 `summary.json`。摘要保留输入 SHA-256、配置、参考长度、统计、循环与 mix 结果，省略完整逐帧数组、landmark 序列和全部事件/信号列表；不是 CLI 完整 `report.json` 的替代 schema。

- `synthetic/`：随工具提供的合成输入。
- `megumin-v9/`：本仓库 `23d31cc4d17c0102f37aba65a650a29868e2556f` 的 v9 数据。
- `original-silent/`：原版参考仓库 `64ed626b7ec9692bc54536b0123fc3cb580c28da` 的 Silent 数据。游戏输入及贴图不随工具分发。

从工具目录重新生成完整 JSON / CSV：

```sh
npm run demo
node bin/spine-audit.mjs --input ../../art/megumin-quartet-spine/actions-v9/export/megumin.json --animations idle_loop,chant_loop,get_up,relaxed_fall,hit,explosion_release --loops idle_loop,chant_loop --transition chant_enter:chant_loop --mix 0.2 --out out-megumin
node bin/spine-audit.mjs --input /your/legal/local/silent.skel --animations idle_loop,attack --loops idle_loop --transition attack:idle_loop --mix 0.2 --out out-silent
```

新结果会使用当前输入，请先比较输入哈希再与基线比较。匹配的同名 atlas 自动加载；原版复现需要自行提供合法本地文件。信号数是点 × 时间 × 指标的记录数，不能当缺陷个数，也不能据此跨角色排名。
