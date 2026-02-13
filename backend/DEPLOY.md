# Web Builder Agent PoC - 部署指南

## 项目结构

```
backend/
├── agentos.py                 # AgentOS 服务入口（Web UI 模式）
├── main.py                    # CLI 模式（命令行测试）
├── requirements.txt           # Python 依赖
├── .env.example               # 环境变量模板
├── .gitignore
├── prompts/
│   └── system_prompt.txt      # 系统提示词
└── skills/
    └── restaurant-menu.yaml   # 示例 Skill
```

## 方式一：Web UI 模式（推荐，公网可访问）

### 1. 克隆仓库

```bash
cd /root
git clone https://github.com/joyboy123456/agno_coding_agent.git webagent
cd /root/webagent/backend
```

### 2. 安装后端依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，填入 API Key：

```
OPENAI_API_KEY=你的金山云API密钥
OPENAI_BASE_URL=https://kspmas.ksyun.com/v1
OPENAI_MODEL=kimi-k2.5
AGENT_HOST=0.0.0.0
AGENT_PORT=7777
```

### 4. 启动后端服务

```bash
cd /root/webagent/backend
python agentos.py
```

后端会在 `0.0.0.0:7777` 启动。

### 5. 安装并启动前端 AgentUI

在 VPS 上另开一个终端：

```bash
cd /root
npx create-agent-ui@latest
# 输入 y 确认，等待安装完成
cd agent-ui
```

修改前端监听地址为 `0.0.0.0`（默认只监听 localhost）：

```bash
# 启动前端，绑定到 0.0.0.0 以便公网访问
HOST=0.0.0.0 npm run dev -- --hostname 0.0.0.0
```

### 6. 公网访问

1. 浏览器打开 `http://<你的VPS公网IP>:3000`
2. 在左侧栏输入后端地址：`http://<你的VPS公网IP>:7777`
3. 选择 "Web Builder Agent" 开始聊天
4. 输入需求，如："帮我做一个饭店菜单网页"

### 7. 防火墙放行（如需要）

```bash
# 放行 7777（后端）和 3000（前端）端口
ufw allow 7777
ufw allow 3000
# 或者用 iptables
iptables -A INPUT -p tcp --dport 7777 -j ACCEPT
iptables -A INPUT -p tcp --dport 3000 -j ACCEPT
```

---

## 方式二：CLI 命令行模式

适合快速测试，不需要前端。

```bash
cd /root/webagent/backend
cp .env.example .env
# 编辑 .env 填入 API Key

# 交互模式
python main.py

# 命令行模式
python main.py restaurant-menu
python main.py restaurant-menu "菜品要包含川菜和粤菜，风格要现代简约"
```

---

## 查看生成结果

生成的项目在 `workspace/` 目录下：

```bash
ls workspace/
cd workspace/<项目目录>/
npm install
npm run dev
```

## 添加新模板

在 `skills/` 目录下创建新的 YAML 文件，格式参考 `restaurant-menu.yaml`。

## 常见问题

**Q: 报错 "请先配置 OPENAI_API_KEY"**
A: 确认 `.env` 文件存在且 `OPENAI_API_KEY` 已填写。

**Q: AgentUI 连不上后端**
A: 确认后端 `agentos.py` 正在运行，且 `AGENT_HOST=0.0.0.0`。检查防火墙是否放行了 7777 端口。

**Q: 公网无法访问前端**
A: 确认前端启动时绑定了 `0.0.0.0`，检查防火墙是否放行了 3000 端口。

**Q: 想用其他 LLM**
A: 修改 `.env` 中的 `OPENAI_BASE_URL` 和 `OPENAI_MODEL` 即可，只要是 OpenAI 兼容接口都支持。
