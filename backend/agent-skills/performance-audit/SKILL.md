---
name: performance-audit
description: 前端性能审计规则集，用于 QA Agent 评估和优化生成项目的性能表现
version: "1.0"
source: 参考 Lighthouse 评分标准和 Web Vitals 指标
---

# Performance Audit Rules

## CRITICAL — Core Web Vitals 目标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| LCP (Largest Contentful Paint) | < 2.5s | 最大内容绘制 |
| FID (First Input Delay) | < 100ms | 首次输入延迟 |
| CLS (Cumulative Layout Shift) | < 0.1 | 累积布局偏移 |
| FCP (First Contentful Paint) | < 1.8s | 首次内容绘制 |
| TTI (Time to Interactive) | < 3.8s | 可交互时间 |

## CRITICAL — 消除 Render-Blocking 资源

- CSS：关键 CSS 应内联到 `<head>` 中，非关键 CSS 异步加载
- JS：第三方脚本使用 `async` 或 `defer` 属性
- 字体：使用 `font-display: swap` 避免 FOIT（不可见文字闪烁）
- 禁止在 `<head>` 中同步加载大型 JS 文件

## HIGH — Bundle 优化

- 生产构建必须启用 Tree Shaking（Vite 默认支持）
- 检查 `npm run build` 输出的 chunk 大小：
  - 单个 JS chunk 不应超过 200KB（gzip 后）
  - 总 JS 体积不应超过 500KB（gzip 后）
- 使用动态 import 做路由级代码分割
- 第三方库考虑 CDN 外部化（如 React、ReactDOM）

## HIGH — 图片优化

- 所有非首屏图片使用 `loading="lazy"`
- 提供明确的 `width` 和 `height` 属性（防止 CLS）
- 优先使用现代格式：WebP > PNG/JPEG
- 装饰性背景优先使用 CSS 渐变或 SVG，而非位图
- 占位图使用低质量模糊预览（LQIP）或纯色占位

## HIGH — CSS 优化

- 使用 Tailwind 的 PurgeCSS（生产构建自动启用）确保未使用的样式被移除
- 避免过深的 CSS 选择器嵌套（不超过 3 层）
- 动画优先使用 `transform` 和 `opacity`（GPU 加速，不触发重排）
- 避免使用 `@import` 导入 CSS（会造成串行加载）

## MEDIUM — JavaScript 优化

- 避免主线程长任务（> 50ms），大计算使用 Web Worker 或分片
- 事件监听器使用 `passive: true`（scroll / touch 事件）
- 防抖/节流高频事件（resize / scroll / input）
- 避免强制同步布局（读写 DOM 属性交替）

## MEDIUM — 缓存策略

- 静态资源文件名包含 content hash（Vite 默认支持）
- 合理设置 Cache-Control 头：
  - 带 hash 的静态资源：`max-age=31536000, immutable`
  - HTML 文件：`no-cache`（始终验证）
- Service Worker 可选（PWA 场景）

## LOW — 预加载与预连接

- 关键资源使用 `<link rel="preload">`（如首屏字体、关键图片）
- 第三方域名使用 `<link rel="preconnect">`（如 CDN、API 域名）
- 下一页导航使用 `<link rel="prefetch">`（可选）

## 审计检查清单

QA Agent 审查时按以下清单逐项检查：

- [ ] `npm run build` 是否成功
- [ ] build 输出的 JS 总体积是否在合理范围
- [ ] 是否存在未使用的大型依赖
- [ ] 图片是否有 lazy loading
- [ ] 是否有 render-blocking 的外部资源
- [ ] CSS 是否使用了 PurgeCSS
- [ ] 动画是否使用了 GPU 加速属性
- [ ] 字体是否设置了 font-display: swap
