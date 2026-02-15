---
name: ui-ux-guidelines
description: 前端 UI/UX 设计规范，用于 QA Agent 审查生成页面的设计质量
version: "1.0"
---

# UI/UX Design Guidelines

## CRITICAL — 语义化 HTML

- 页面必须使用正确的语义标签结构：
  - `<header>` 页头 / `<nav>` 导航 / `<main>` 主内容 / `<footer>` 页脚
  - `<section>` 独立区块 / `<article>` 独立内容 / `<aside>` 侧边栏
- 标题层级必须连续（h1 → h2 → h3），禁止跳级
- 每个页面有且仅有一个 `<h1>`
- 交互元素必须使用正确标签：按钮用 `<button>`，链接用 `<a>`，禁止用 `<div>` 模拟

## CRITICAL — 可访问性 (a11y)

- 所有图片必须有 `alt` 属性（装饰性图片用 `alt=""`）
- 表单控件必须关联 `<label>`（通过 `htmlFor` 或嵌套）
- 交互元素必须可键盘访问（Tab 导航、Enter/Space 触发）
- 颜色不能作为传达信息的唯一方式（需配合文字/图标）
- 对比度：正文文字与背景的对比度 >= 4.5:1，大文字 >= 3:1
- 焦点状态必须可见（禁止 `outline: none` 不提供替代）

## HIGH — 响应式布局

- 采用 Mobile-First 策略，基础样式面向移动端
- 推荐断点（Tailwind 默认）：
  - `sm`: 640px（大手机/小平板）
  - `md`: 768px（平板）
  - `lg`: 1024px（笔记本）
  - `xl`: 1280px（桌面）
- 导航栏在移动端必须折叠为汉堡菜单或底部导航
- 卡片/网格布局在移动端必须单列显示
- 触摸目标最小尺寸 44x44px
- 禁止水平滚动（除非是有意设计的横向滚动区域）

## HIGH — 视觉一致性

- 颜色系统：使用 Tailwind 的颜色变量或 CSS 自定义属性，禁止硬编码颜色值散落各处
- 字体层级：标题/正文/辅助文字的字号、字重、行高必须统一
- 间距系统：使用 Tailwind 的间距 scale（4px 基准），保持一致的 padding/margin
- 圆角：全局统一圆角大小（如 rounded-lg），不要混用多种圆角
- 阴影：统一阴影层级（如 shadow-sm / shadow-md），不要随意自定义

## MEDIUM — 微交互

- 按钮/卡片/链接必须有 hover 状态变化（颜色、阴影或 transform）
- 状态切换使用 CSS transition（推荐 150-300ms）
- 页面/组件入场可使用淡入或滑入动画（不强制，但推荐）
- 加载状态使用 skeleton 或 spinner，禁止空白等待
- 动画不得影响可用性（尊重 `prefers-reduced-motion`）

## MEDIUM — 图标规范

- 所有 UI 图标必须使用 SVG（内联 SVG 或 SVG 组件）
- 禁止使用 emoji 作为 UI 图标元素
- SVG 图标应支持 currentColor 以适配主题切换
- 图标尺寸与文字对齐，推荐 16px / 20px / 24px 三档

## LOW — 空状态与反馈

- 列表为空时显示友好的空状态提示（图标 + 文字 + 可选操作按钮）
- 表单提交后显示成功/失败反馈
- 网络错误显示重试按钮
- 长操作显示进度指示
