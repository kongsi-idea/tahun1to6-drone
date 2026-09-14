# Handoff — 飞学竞场

## 收工状态 · 2026-09-14

最新用户已确定 slug 为 `tahun1to6-drone`，并明确授权部署到 Vercel `kongsi-idea` 团队与 Hub 上架。Hub 本地已备妥 `?tool=tahun1to6-drone` 详情深链接和复制分享按钮、待上线登记与跨年级学科筛选。Vercel API DNS 不通，线上发布未完成；源码仍在本目录。旧建议 slug 全被 `tahun1to6-drone` 取代。

### 最新细修：选项箭头与题卡

坐标表已移除。四个选项现在各有 A/B/C/D 环标与跟随玩家朝向实时旋转的箭头，答案全文放在题卡；题卡分学科／年级标签、题目、思考倒数进度和选项，手机横屏单独缩排。答错移除对应箭头，清题一并清除；答题隐藏“找环”按钮。新增 `.vercelignore` 排除测试与交接档。

Hub 名称仍为「飞学竞场」，建议马来文名 `Arena Terbang Ilmu`；跨年级跨学科的 Vercel slug 建议 `tahun1-6-gabungan-terbang-ilmu`，目标 team 为 `kongsi-idea`。这是对既有单年级／单科目命名的扩展，尚未建立远端项目、移动源码或上架。当前服务启动再次被端口权限拒绝，浏览器验收未完成。后续仍须修复题库质量与去重、真正地图大小选择等旧版遗留问题，不能将此前“第二轮完成”视为全部六项需求通过验收。

产品暂定名已改为「飞学竞场」——定位是飞行学习挑战，不再仅限无人机竞速或心算。已依 Yong Quan 的试玩反馈完成第二轮玩法代码：首次访问直接进入五段飞行试炼，完成后才显示主画面；完成状态只存本机，回访者不再重做。主画面可选 Tahun 1–6、综合／数学／科学／Bahasa Melayu／English／华文（Tahun 4 起另有 Sejarah）及近场／标准／远征地图。

答题现为两段式：先显示学科题目 7 秒，让学生自由飞行收集能量环得积分；之后才把所有答案环随机散布到不同方位。竞赛答题刻意关闭单一「目标」箭头、最近环导航与自动瞄准；改为显示每一个选项的方向、距离和 X/Z 坐标。远征地图将赛道半径扩大 1.82 倍。题库是按低／高年段分层的起始包，含即时生成数学题与 1–6 年级各学科种子题；它不是已经逐项认证的正式 DSKP 题库，发布前需由教师审核、再按单元扩充。

已更新 `tests/test_game.py`：新增首访直入试炼、思考阶段无答案环、答案揭示后无正确目标、方位表及四环散布检查；保留原有三视口、双触点、暂停、穿环、结算与储存覆盖。页面 JS 已经 `node --input-type=module --check` 通过，Python 测试脚本可编译。当前 Codex 沙盒仍拒绝绑定 `8746`（`PermissionError: Operation not permitted`），所以这轮无法在此环境跑浏览器回归或重做真实 iPhone／Safari 验证；请在普通 Terminal 启动 `./run.sh` 后实测。

没有外部发布、依赖安装、Git commit、数据库或环境设定改动。

主要文件：`index.html`、`manifest.json`、`icon.svg`、`tests/test_game.py`。持久项目规则在 `agents.md`；原始源码备份和可清理的浏览器截图在 `../playwright-to-delete/drone-upgrade/`。
