---
name: daily-60s-news-poster
description: generate a wechat-friendly daily news poster image in chinese (similar to “每天60s读懂世界”), including a numbered one-line news list (default top 15), plus a text version with citations. use when the user asks for a daily news poster/long image/海报/长图, “60s读懂世界”, daily headlines image, or wants a shareable image summarizing today’s news.
---

# Daily 60s News Poster

你要生成一张**可分享的每日新闻长图海报**（默认 1080×1920），风格类似「每天 60s 读懂世界」，并同时输出**文字版（带 citations）**。

## 核心规则
- **必须使用 web.run** 获取最新新闻（默认窗口：过去 24–48 小时）。
- **每条要点至少 2 个高质量来源**（官方公告可放宽为 1 个官方来源）。来源标准见：`references/source-standards.md`。
- **去重聚类**：同一事件多家媒体报道合并为 1 条。
- **一句话要点**遵循：`references/rewriting-rules.md`。
- **海报图片不放 citations**；cites 只在文字版输出。

## 默认输出
1) **文字版**：Top 15（可按用户要求改为 Top 10 / Top 20）
- 每条包含：标题（一句话要点）、发生了什么（2句内）、为什么重要（1句）、影响区域、来源（2–3 个 citations）

2) **海报 PNG**：单列 15 条 + 标题/日期/星期/页脚来源

## 工作流（必须按顺序）

### 1) 设定范围
- 若用户未指定日期：用“今天”（以用户时区为准）。
- 若用户未指定条数：默认 15 条。
- 若用户要求分栏（国内/国外）：先生成结构化列表，再决定是否改模板（默认单列）。

### 2) 搜集新闻（web.run）
建议至少 3–4 个 query 覆盖：
- 国内要闻（政策/社会）
- 国际（冲突/外交）
- 财经市场（油价/汇率/股债）
- 科技（AI/大厂发布）

### 3) 去重与排序
- 合并近重复事件（同一地点同一政策/同一冲突进展等）。
- 用“影响力/覆盖面/紧迫性/时效性”粗略排序；对快变事件可加一条“最新进展”。

### 4) 写文字版（带 citations）
按下列结构输出：
- **今日 60s 新闻要点（YYYY-MM-DD）**
- 1–15 条，每条包含：
  - **要点**（一句话）
  - 发生了什么（2句）
  - 为什么重要（1句）
  - 影响区域
  - 来源：2–3 个 citations

### 5) 渲染海报图片（HTML + Puppeteer）
- 先把榜单写成 `raw_list.json`：
  - `date`：YYYY-MM-DD
  - `items`：[{rank, text, sources}, ...]
  - `meta`：lunar/signature/sources/updated_at
- 运行 `scripts/build_payload.py` 生成 `payload.json`。
- 再用 `scripts/render_poster.js`（Puppeteer）渲染 PNG。

#### 依赖说明
- 渲染脚本需要 Node.js + puppeteer。
- 若 puppeteer 不存在，在技能目录下执行：
  - `npm init -y`
  - `npm i puppeteer`

#### 输出文件命名
- `poster_YYYYMMDD.png`

## 参考
- 样式规范：`references/style-spec.md`
- 来源标准：`references/source-standards.md`
- 改写规则：`references/rewriting-rules.md`
- HTML 模板：`templates/poster.html`
- 渲染脚本：`scripts/render_poster.js`
