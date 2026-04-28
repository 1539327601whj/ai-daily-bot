# MEMORY.md - 长期记忆

## 项目架构（已确定）

| 组件 | 技术选型 | 部署平台 |
|------|----------|----------|
| 前端 | React + Vite | Vercel |
| 后端 | Spring Boot 3.2 + MyBatis-Plus | Render |
| 数据库 | TiDB Serverless | tidb.cloud |
| AI 爬虫 | Python + GitHub Actions | GitHub |

## TiDB 连接信息

- Host: gateway01.us-west-2.prod.aws.tidbcloud.com
- Port: 4000
- User: 2mdpH9MkQ28H3P9.root
- Database: ai_daily
- Password: YsjDMvZ0Sj7GvoTo

## 部署文件

- `backend/Dockerfile` - Render 容器部署
- `backend/render.yaml` - Render 蓝图配置
- `frontend/vercel.json` - Vercel API 代理
- `backend/sql/init_tidb.sql` - 数据库初始化脚本
- `DEPLOY.md` - 完整部署指南

## 技术偏好

- 用户偏好中文交流
- 沟通简洁行动导向
- commit message 简洁明了
- 常用表格对比信息

## 踩坑记录

| 时间 | 问题 | 原因 | 解决方案 |
|------|------|------|----------|
| 2026-04-28 | 前端显示"已生成简报 0" | MyBatis-Plus 缺少分页插件配置 | 创建 `MybatisPlusConfig.java` 添加分页插件 |
| 2026-04-28 | 修复后仍显示 0 | `MybatisPlusConfig.java` 创建在了错误的目录 | 移动到正确的 `backend/src/main/java/...` 目录 |
| 2026-04-28 | Vercel 构建失败 (TS6133) | 存在未使用的 import 和变量 | 移除未使用的 `React`, `dayjs`, `latest`, `navigate` 声明 |
| 2026-04-28 | 400 input length too long | AI prompt 内容超过 token 限制 | `buildContext()` 改用 summary 并限制 500 字符/条 |

## 关键经验

- **MyBatis-Plus 3.5+ 分页**：需要显式配置 `MybatisPlusInterceptor` + `PaginationInnerInterceptor`，否则 `Page.getTotal()` 返回 0
- Render 部署需要几分钟检测 Git push 并自动重新部署
- **项目目录结构**：`/d/programme/WorkBuddy/project/` 是项目根目录，包含 `backend/` (后端)、`frontend/` (前端) 等
- **Vercel 部署**：使用 `npx vercel --prod --yes` 部署，注意 TypeScript 严格模式下未使用的变量会导致构建失败

## 部署状态 (2026-04-28)

| 平台 | 状态 | URL |
|------|------|-----|
| 后端 | ✅ 运行中 | https://ai-daily-bot.onrender.com |
| 前端 | ✅ 已部署 | https://frontend-pearl-phi-70.vercel.app |
