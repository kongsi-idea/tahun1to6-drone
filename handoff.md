# Handoff — 飞学竞场

## ⏯️ 目前做到哪

已发布上线（`https://tahun1to6-drone.vercel.app`，Hub 已上架）并加了班级排行榜。排行榜代码已部署，但 Supabase 数据表还没建——**唯一卡住的一步等 Yong Quan**。

## 🚦 目前状态

- 游戏本体：可玩，老师已实测确认没问题。
- 班级排行榜：UI/交互全部完成并实测通过（含一个真 bug 修复），但数据库表 `tahun1to6_drone_scores` 尚未建立，所以现在读写会静默失败（不影响游戏，只是排行榜暂时是空的）。
- 题库仍是待审起始包，尚未经教师逐条核对课本/DSKP。

## ➡️ 下一步

1. **Yong Quan**：把 `kongsi-idea/supabase/migration-2026-09-14-tahun1to6-drone-scores.sql` 贴到 Supabase Dashboard（项目 `gntnkhkkgonaehapcerr`）的 SQL Editor 执行一次。
2. 执行完通知 agent，用真实班级代码走一遍完整提交/查榜流程再确认。
3. 之后：题库仍需教师审核＋扩充；真实 iOS Safari／「添加到主屏幕」验证仍未做。

## ⚠️ 注意事项

- **`python3 tests/test_game.py` 在 Claude Code 沙盒里会 timeout**（`wait_for_function` 等不到 `window.__gameReady`），已用 `git stash` 切回上一版验证过是沙盒本身的环境限制、不是代码问题；请在**普通 Terminal** 里跑。
- 这个工具**没有接 GitHub 自动部署**（`vercel link` 时连接失败），push 之后要记得手动 `vercel deploy --prod`。
- 排行榜分页按钮一度跟游戏「穿环竞速／答题竞速」切换器共用 CSS class（`.mode-btn`）撞在一起，点分页会把游戏模式设成 `undefined`——已改名 `.board-tab` 修好，`tests/test_game.py` 加了回归检查。

## 🕐 最后更新

2026-09-14 下午 · Claude (Sonnet 5) @ 这台 Mac · Git：✅ 已推（drone-soccer + kongsi-idea 两个仓库都已 commit + push + 生产部署）

---

## 历史摘要

- 2026-09-14 上午：第二轮玩法完成（五段飞行试炼、跨学科答题两段式、方向箭头取代坐标表），经老师试玩确认后发布上线（slug `tahun1to6-drone`，Vercel `kongsi-idea` 团队）。
- 2026-08 前身：从「无人机足球」原型迭代为「飞学竞场」，早期版本细节见 Git 历史。

持久项目规则（技术边界、不能破坏的规则、关键决定）在 `agents.md`；浏览器临时截图在 `../playwright-to-delete/`。
