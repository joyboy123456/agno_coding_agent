# Web Builder Agent PoC - 部署指南

## 快速开始（在 VPS 上执行）

### 1. 创建项目目录

```bash
mkdir -p /root/webagent/backend
```

### 2. 上传文件

将以下文件上传到 VPS 的 `/root/webagent/backend/` 目录：

```
backend/
├── main.py                    # Agent 主脚本
├── requirements.txt           # Python 依赖
├── .env.example               # 环境变量模板
├── .gitignore
├── prompts/
│   └── system_prompt.txt      # 系统提示词
└── skills/
    └── restaurant-menu.yaml   # 示例 Skill
```

### 3. 安装依赖

```bash
cd /root/webagent/backend
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，填入你的 API Key：

```
OPENAI_API_KEY=你的金山云API密钥
OPENAI_BASE_URL=https://kspmas.ksyun.com/v1
OPENAI_MODEL=kimi-k2.5
```

### 5. 运行

**交互模式（推荐首次使用）：**

```bash
python main.py
```

会显示可用模板列表，选择后输入补充需求即可。

**命令行模式：**

```bash
# 使用餐厅菜单模板
python main.py restaurant-menu

# 带补充需求
python main.py restaurant-menu "菜品要包含川菜和粤菜，风格要现代简约"
```

### 6. 查看结果

生成的项目在 `workspace/<run_id>/` 目录下。

```bash
# 查看生成的文件
ls workspace/

# 进入生成的项目，手动验证
cd workspace/<run_id>/
npm install
npm run dev
```

## 添加新模板

在 `skills/` 目录下创建新的 YAML 文件，格式参考 `restaurant-menu.yaml`。

## 常见问题

**Q: 报错 "请先配置 OPENAI_API_KEY"**
A: 确认 `.env` 文件存在且 `OPENAI_API_KEY` 已填写。

**Q: Agent 生成的代码有问题**
A: Agent 会自动执行 `npm install && npm run build` 自检，失败会尝试修复（最多 2 次）。如果仍然失败，检查 `debug_mode=True` 的日志输出。

**Q: 想用其他 LLM**
A: 修改 `.env` 中的 `OPENAI_BASE_URL` 和 `OPENAI_MODEL` 即可，只要是 OpenAI 兼容接口都支持。
