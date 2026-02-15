# Agno Coding Agent

基于 [Agno](https://github.com/agno-agi/agno) 框架的网页生成编程 Agent 系统。选择模板、补充需求，Agent 自动生成可运行的前端网页项目。

## 特性

- **多 Agent 协作** — Developer Agent 生成代码，QA Agent 审查质量，Workflow 编排全流程
- **模板驱动** — YAML 格式的 Skill 模板，定义页面结构、交互、约束和验收标准
- **自动质量审查** — 四维度审查（React 最佳实践、UI/UX、性能、可访问性），自动修复 critical 问题
- **结构化交付** — 输出严格 JSON，包含项目路径、技术栈、QA 评分等信息
- **双运行模式** — CLI 命令行 + Web UI 聊天界面
- **多模型支持** — 兼容 OpenAI 接口的任意模型（GPT / GLM / Kimi 等）

## 架构

```
用户需求 → Skill 模板匹配 → Developer Agent 生成项目
                                      ↓
                              QA Agent 审查代码
                                      ↓
                            条件修复 → 结构化交付 JSON
```

| 层级 | 说明 | 技术栈 |
|------|------|--------|
| 前端 | 聊天式交互界面 | Next.js 15 + React 18 + Tailwind CSS |
| 后端 | Agent 编排服务 | Python + Agno + FastAPI |
| 执行层 | 代码生成 + 质量审查 | Developer Agent + QA Agent + Workflow |

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- pnpm

### 安装

```bash
git clone https://github.com/joyboy123456/agno_coding_agent.git
cd agno_coding_agent

# 配置 API Key
cp backend/.env.example backend/.env
# 编辑 backend/.env，填入你的 LLM API Key

# 一键安装前后端依赖
make install
```

### 启动开发环境

```bash
# 一键启动前后端（后端 :7777 + 前端 :3000）
make dev
```

后端自动热重载，前端自动热更新，`Ctrl+C` 停止所有服务。

### CLI 模式

```bash
# 交互模式（选择模板 + 输入需求）
make cli

# 直接运行指定模板
make run SKILL=restaurant-menu
```

## 常用命令

| 命令 | 说明 |
|------|------|
| `make dev` | 一键启动前后端开发环境 |
| `make dev-backend` | 仅启动后端 |
| `make dev-frontend` | 仅启动前端 |
| `make install` | 安装前后端依赖 |
| `make cli` | CLI 交互模式 |
| `make run SKILL=<id>` | 运行指定模板 |
| `make stop` | 停止所有服务 |
| `make clean` | 清理临时文件 |

## 项目结构

```
agno_coding_agent/
├── backend/
│   ├── agents/              # Agent 定义
│   │   ├── developer.py     # Developer Agent（代码生成）
│   │   ├── qa.py            # QA Agent（质量审查）
│   │   └── workflow.py      # 多 Agent 协作编排
│   ├── skills/              # Skill 模板库（YAML）
│   ├── agent-skills/        # QA 专业知识库
│   ├── prompts/             # 系统提示词
│   ├── models/              # 数据模型（Pydantic）
│   ├── agentos.py           # Web UI 服务入口
│   ├── main.py              # CLI 入口
│   └── workspace/           # 生成项目存放目录
├── agent-ui/                # 前端 Web UI（Next.js）
├── Makefile                 # 开发命令集
└── CLAUDE.md                # AI 上下文文档
```

## 环境变量

在 `backend/.env` 中配置：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `OPENAI_API_KEY` | LLM API 密钥 | 必填 |
| `OPENAI_BASE_URL` | LLM API 地址 | `https://kspmas.ksyun.com/v1` |
| `OPENAI_MODEL` | 默认模型 ID | `kimi-k2.5` |
| `AGENT_HOST` | 服务监听地址 | `0.0.0.0` |
| `AGENT_PORT` | 服务监听端口 | `7777` |

## 已有模板

| Skill ID | 名称 | 描述 |
|----------|------|------|
| `restaurant-menu` | 餐厅菜单网页 | 分类浏览、菜品详情、响应式布局 |

新增模板：在 `backend/skills/` 下创建 YAML 文件，参考 `restaurant-menu.yaml`。

## 技术依赖

**后端：** Agno 2.2.13 / FastAPI / SQLAlchemy / PyYAML / python-dotenv

**前端：** Next.js 15 / React 18 / Tailwind CSS / Zustand / Radix UI / Framer Motion

## License

MIT
