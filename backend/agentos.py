"""
Web Builder Coding Agent - AgentOS 服务入口（Web UI 模式）
通过 AgentOS 暴露 Agent，配合 AgentUI 前端提供公网可访问的聊天界面
"""
import os
import uuid
import yaml
from pathlib import Path
from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.openai.like import OpenAILike
from agno.tools.shell import ShellTools
from agno.tools.file import FileTools
from agno.os import AgentOS
from agno.db.sqlite import SqliteDb

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY", "")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://kspmas.ksyun.com/v1")
MODEL_ID = os.getenv("OPENAI_MODEL", "kimi-k2.5")
HOST = os.getenv("AGENT_HOST", "0.0.0.0")
PORT = int(os.getenv("AGENT_PORT", "7777"))

BASE_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = BASE_DIR / "prompts"
SKILLS_DIR = BASE_DIR / "skills"
WORKSPACE_DIR = BASE_DIR / "workspace"
DB_DIR = BASE_DIR / "tmp"

# 确保目录存在
WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# 加载系统提示词和 Skill 信息
# ---------------------------------------------------------------------------

def load_system_prompt() -> str:
    """加载系统提示词"""
    path = PROMPTS_DIR / "system_prompt.txt"
    return path.read_text(encoding="utf-8") if path.exists() else ""


def load_all_skills_info() -> str:
    """加载所有 Skill 信息，拼接到 instructions 中"""
    if not SKILLS_DIR.exists():
        return ""
    parts = []
    for f in SKILLS_DIR.glob("*.yaml"):
        with open(f, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
            parts.append(f"- {data.get('id', f.stem)}: {data.get('name', '')} — {data.get('description', '')}")
    return "\n".join(parts)


def build_runtime_instructions() -> list[str]:
    """构建运行时指令，注入到 Agent 的 instructions 中"""
    skills_info = load_all_skills_info()

    return [
        "你是【网页生成编程 Agent】(Web Builder Coding Agent)。",
        "你的唯一目标：根据用户需求，在工作目录中生成一个可运行的前端网页项目。",
        "",
        "## 工作目录",
        f"所有文件操作必须在 {WORKSPACE_DIR} 下进行。",
        "每次生成任务请先创建一个子目录作为项目根目录。",
        "",
        "## 可用模板（Skills）",
        skills_info if skills_info else "（暂无模板）",
        "",
        "## 用户交互流程",
        "1. 用户描述需求（如：帮我做个饭店菜单网页）",
        "2. 你根据需求匹配合适的模板，或自由发挥",
        "3. 制定计划（功能点、页面结构、目录结构）",
        "4. 使用 FileTools 创建项目文件",
        "5. 使用 ShellTools 执行 npm install && npm run build 自检",
        "6. 如果自检失败，修复并重试（最多 2 次）",
        "7. 最终输出交付 JSON",
        "",
        "## 技术栈默认值",
        "- 框架: Vite + React + Tailwind CSS",
        "- 包管理器: npm",
        "- 构建命令: npm run build",
        "",
        "## 输出契约（最终必须输出的 JSON）",
        '{"run_title": "项目名", "stack": "技术栈", "how_to_run": ["npm install", "npm run dev"], '
        '"features": ["功能1"], "self_check": {"result": "pass|fail", "notes": "摘要"}}',
        "",
        "## 约束",
        "- 禁止使用 emoji 作为 UI 图标，必须使用 SVG",
        "- 禁止调用需要密钥的外部服务",
        "- 优先少依赖、轻量实现",
        "- 默认使用中文输出",
    ]


# ---------------------------------------------------------------------------
# 创建 Agent
# ---------------------------------------------------------------------------

web_builder_agent = Agent(
    name="Web Builder Agent",
    model=OpenAILike(
        id=MODEL_ID,
        api_key=API_KEY,
        base_url=BASE_URL,
    ),
    description="网页生成编程 Agent — 根据你的需求生成可运行的前端网页项目",
    instructions=build_runtime_instructions(),
    tools=[
        ShellTools(base_dir=WORKSPACE_DIR),
        FileTools(base_dir=WORKSPACE_DIR),
    ],
    # 会话持久化
    db=SqliteDb(db_file=str(DB_DIR / "agents.db")),
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
    debug_mode=True,
)

# ---------------------------------------------------------------------------
# AgentOS 服务
# ---------------------------------------------------------------------------

agent_os = AgentOS(agents=[web_builder_agent])
app = agent_os.get_app()

if __name__ == "__main__":
    if not API_KEY or API_KEY == "your-api-key-here":
        print("[错误] 请先配置 OPENAI_API_KEY")
        print("  1. 复制 .env.example 为 .env")
        print("  2. 填入你的 API Key")
        exit(1)

    print(f"\n{'='*60}")
    print(f"  Web Builder Agent - AgentOS 服务")
    print(f"  后端地址: http://{HOST}:{PORT}")
    print(f"  前端连接: 在 AgentUI 中输入 http://<你的VPS公网IP>:{PORT}")
    print(f"{'='*60}\n")

    agent_os.serve(app="agentos:app", host=HOST, port=PORT, reload=True)
