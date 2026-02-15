"""
Web Builder Coding Agent - AgentOS 服务入口（Web UI 模式）
通过 AgentOS 暴露 Agent，配合 AgentUI 前端提供公网可访问的聊天界面

v2: Developer Agent 对外暴露，QA Agent 在 Workflow 中后台运行
    AgentOS 模式下仍使用单 Agent 对话体验（对用户透明），
    CLI 模式使用完整 Workflow（Developer + QA）。
"""
import os
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
load_dotenv(override=True)

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


def build_system_message() -> str:
    """构建完整的 system_message：系统提示词 + 运行时上下文 + Skills 信息"""
    # 加载宪法级系统提示词
    base_prompt = load_system_prompt()

    # 拼接运行时上下文
    skills_info = load_all_skills_info()

    runtime_section = f"""

====================
运行时上下文（AgentOS 模式）
====================
- 工作目录: {WORKSPACE_DIR}
- 每次生成任务请先在工作目录下创建一个子目录作为项目根目录
- 默认技术栈: Vite + React + Tailwind CSS
- 包管理器: npm
- 构建命令: npm run build

可用模板（Skills）:
{skills_info if skills_info else "（暂无模板）"}

用户交互流程:
1. 用户描述需求（如：帮我做个饭店菜单网页）
2. 你根据需求匹配合适的模板，或自由发挥
3. 按照系统提示词中的四阶段工作流执行
4. 必须使用工具（FileTools / ShellTools）真正创建文件和执行命令
5. 禁止跳过工具调用直接编造交付 JSON
"""

    return base_prompt + runtime_section


# ---------------------------------------------------------------------------
# 创建多个 Agent（不同模型，AgentUI 中可切换）
# ---------------------------------------------------------------------------

def create_agent(name: str, model_id: str, description: str) -> Agent:
    """工厂函数：创建指定模型的 Web Builder Agent"""
    return Agent(
        name=name,
        model=OpenAILike(
            id=model_id,
            api_key=API_KEY,
            base_url=BASE_URL,
        ),
        description=description,
        system_message=build_system_message(),
        tools=[
            ShellTools(base_dir=WORKSPACE_DIR),
            FileTools(base_dir=WORKSPACE_DIR),
        ],
        add_datetime_to_context=True,
        add_history_to_context=True,
        num_history_runs=5,
        markdown=True,
        debug_mode=True,
    )

# 主力模型
agent_codex = create_agent(
    name="Web Builder (GPT-5.3-Codex)",
    model_id="gpt-5.3-codex",
    description="代码专用模型 — function calling 强，适合生成完整网页项目",
)

# 备选模型
agent_glm = create_agent(
    name="Web Builder (GLM-5)",
    model_id="glm-5",
    description="智谱 GLM-5 — 中文理解强，适合中文网页需求",
)

agent_kimi = create_agent(
    name="Web Builder (Kimi-K2.5)",
    model_id="kimi-k2.5",
    description="Kimi K2.5 — 长上下文，适合复杂需求分析",
)

# ---------------------------------------------------------------------------
# AgentOS 服务（注册所有 Agent，UI 中可切换）
# ---------------------------------------------------------------------------

agent_os = AgentOS(
    agents=[agent_codex, agent_glm, agent_kimi],
    db=SqliteDb(db_file=str(DB_DIR / "agents.db")),
)
app = agent_os.get_app()

if __name__ == "__main__":
    if not API_KEY or API_KEY == "your-api-key-here":
        print("[错误] 请先配置 OPENAI_API_KEY")
        print("  1. 复制 .env.example 为 .env")
        print("  2. 填入你的 API Key")
        exit(1)

    print(f"\n{'='*60}")
    print(f"  Web Builder Agent v2 - AgentOS 服务")
    print(f"  模式: Developer Agent (AgentOS) + QA Agent (后台)")
    print(f"  后端地址: http://{HOST}:{PORT}")
    print(f"  前端连接: 在 AgentUI 中输入 http://<你的VPS公网IP>:{PORT}")
    print(f"{'='*60}\n")

    agent_os.serve(app="agentos:app", host=HOST, port=PORT, reload=True)
