# Handoff — 飞学竞场

## 班级排行榜 · 2026-09-14 下午

老师确认发布并要求加排行榜后，用 EnterPlanMode 走完一轮设计确认（三个决定：限本班接 kelasku 登入、真实姓名、穿环竞速＋答题竞速两张榜）。已实作并部署：

- 网址带 `?code=` 班级代码（或本机记住过）时，进场前弹「选你的名字」（复用 `kongsi-idea` 的 `ClassCode`/`supabaseClient`，跟 `tahun1-bc-bishun` 同一套；查无名单会自动退回手动输入名字），完成后主画面出现「🏆 班级排行榜」按钮。没有 `?code=` 的一般访客完全不受影响，已用 Playwright 实测确认（identity-screen/leaderboard-btn 都保持隐藏，`student` 是 `null`）。
- 排行榜表 `tahun1to6_drone_scores` + RPC `submit_tahun1to6_drone_score`：`kongsi-idea/supabase/migration-2026-09-14-tahun1to6-drone-scores.sql`——**这份 SQL 还没有人跑，需要 Yong Quan 手动贴到 Supabase Dashboard SQL Editor 执行一次**（这个专案没有 CLI/MCP 写入权限，已用 `which supabase psql` 确认过这台机器上两者都不存在，不是偷懒跳过）。migration 跑之前，排行榜按钮和面板功能都正常显示，只是读/写会因表不存在而静默失败（已用 Playwright 实测确认 404 会被 catch 住，不会白屏或报未捕获错误）。
- **实测抓到一个真 bug 并已修好**：一开始把排行榜分页按钮的 class 取名 `mode-btn`，结果跟游戏本身「穿环竞速／答题竞速」切换器共用的**全局** `document.querySelectorAll(".mode-btn")` 点击监听器撞在一起——点排行榜分页会把 `state.mode` 设成 `undefined`，导致比赛结算画面读成答题模式的文案。已改名 `.board-tab` 并补对应 CSS 解决，`tests/test_game.py` 新增了这条回归断言（`leaderboard tab click must not touch game mode`）。
- 本机 `python3 tests/test_game.py` 在这个 Claude Code 沙盒里**持续 timeout**（`Page.wait_for_function` 等不到 `window.__gameReady`），但直接改用 Playwright MCP 交互式浏览器验证（同样是 headless Chromium）反而每次都秒过——用 `git stash` 切回上一版 `aa058c1`（今天稍早已上线、已过老师实测的版本）重跑同一份测试，**同样 timeout**，证明这是这台沙盒本身的环境限制，不是这次改动引入的问题。新增的两段测试代码已写入 `tests/test_game.py`，请在**普通 Terminal**（不是这个沙盒）里跑一次确认。
- 已用 Playwright 实测：无 code 默认路径干净、`?code=` 未知班级会走手动输入 fallback、选完名字排行榜按钮出现、排行榜面板两个分页能切换且不影响游戏本身的模式、穿环竞速真的跑完一局后结算文案正确显示「环」而不是「分」、手机 390×844 视口下身份卡片与排行榜卡片都没有溢出。**没有测试过**：migration 跑完之后的真实读写往返（因为还没跑）、真实 iPhone Safari。
- 代码已 commit 并 `vercel deploy --prod`（这个工具没接 GitHub 自动部署，一直都要手动跑这一步）。

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
