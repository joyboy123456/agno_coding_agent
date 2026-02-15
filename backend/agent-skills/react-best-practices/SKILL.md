---
name: react-best-practices
description: React 与前端工程最佳实践规则集，按影响分级，用于 QA Agent 代码审查
version: "1.0"
source: 改编自 Vercel react-best-practices（40+ 规则）
---

# React Best Practices

审查时按以下规则逐条检查，每条标注了影响等级。

## CRITICAL — 消除异步瀑布流

- **C1**: 不相互依赖的 async 操作必须用 `Promise.all()` 并行执行，禁止串行 await
  ```tsx
  // BAD
  const user = await fetchUser(id);
  const posts = await fetchPosts(id); // 不依赖 user，却等 user 完成

  // GOOD
  const [user, posts] = await Promise.all([fetchUser(id), fetchPosts(id)]);
  ```

- **C2**: 提前返回（early return）避免不必要的 await
  ```tsx
  // BAD
  async function handle(id, skip) {
    const data = await fetchData(id);
    if (skip) return { skipped: true }; // 白等了
  }

  // GOOD
  async function handle(id, skip) {
    if (skip) return { skipped: true };
    const data = await fetchData(id);
    return process(data);
  }
  ```

- **C3**: 避免在循环中串行 await，改用 `Promise.all(items.map(...))`

## CRITICAL — 减小 Bundle 体积

- **C4**: 禁止 barrel import 整个库
  ```tsx
  // BAD
  import { Button } from '@/components';

  // GOOD
  import { Button } from '@/components/Button';
  ```

- **C5**: 大型库必须按需导入
  ```tsx
  // BAD
  import _ from 'lodash';

  // GOOD
  import debounce from 'lodash/debounce';
  ```

- **C6**: 路由级组件必须使用 `React.lazy()` + `Suspense` 做代码分割

- **C7**: 仅客户端使用的重型库（如图表库）必须动态导入

## HIGH — 组件与状态管理

- **H1**: 组件遵循单一职责，超过 200 行应考虑拆分
- **H2**: 状态就近原则：state 放在最近的需要它的组件中，避免不必要的提升
- **H3**: 避免 prop drilling 超过 3 层，考虑 Context 或组合模式
- **H4**: 列表渲染必须提供稳定的 `key`（禁止用 index 作为 key，除非列表不会变化）
- **H5**: 表单状态优先使用非受控组件 + `useRef`，减少重渲染

## HIGH — Hook 使用规范

- **H6**: `useEffect` 依赖数组必须完整且正确
- **H7**: 禁止级联 useEffect（一个 effect 设置 state 触发另一个 effect）
- **H8**: 数据获取优先使用专用库（SWR / React Query），而非裸 useEffect
- **H9**: `useMemo` / `useCallback` 仅在有明确性能收益时使用，不要过度优化

## MEDIUM — 渲染优化

- **M1**: 避免在 JSX 中内联创建对象/数组（每次渲染都创建新引用）
- **M2**: 事件处理函数避免在 render 中用箭头函数创建（高频组件中）
- **M3**: 条件渲染优先使用 `&&` 或三元，避免不必要的组件挂载/卸载
- **M4**: 长列表使用虚拟滚动（react-window / react-virtuoso）

## LOW — 代码风格

- **L1**: 组件文件命名使用 PascalCase
- **L2**: 工具函数/hooks 文件命名使用 camelCase
- **L3**: 类型定义与组件分离，放在独立的 types.ts 中
- **L4**: 常量提取到文件顶部或独立的 constants.ts 中
