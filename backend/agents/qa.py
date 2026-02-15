"""
Web Builder Agent - QA Agent 定义
独立的前端代码质量审查 Agent，负责：
1. 代码质量审查（React 最佳实践）
2. UI/UX 设计审查（语义化、响应式、可访问性）
3. 性能审查（bundle 优化、加载性能）
4. 直接修复 critical 级别问题

通过加载 agent-skills/ 目录下的专业知识增强审查能力。
"""
import os
from pathlib import Path

from agno.agent import Agent
from agno.models.openai.like import OpenAILike
from agno.tools.file import FileTools
from agno.tools.shell import ShellTools

from models.schemas import QAReport


# ---------------------------------------------------------------------------
# 路径常量
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
PROMPTS_DIR = BASE_DIR / "prompts"
AGENT_SKILLS_DIR = BASE_DIR / "agent-skills"


# ---------------------------------------------------------------------------
# Skills 加载
# ---------------------------------------------------------------------------

def load_agent_skills() -> str:
    """
    加载 agent-skills/ 目录下所有 SKILL.md 的内容，
    拼接成一段完整的知识文本注入到 QA Agent 的 instructions 中。
    """
    if not AGENT_SKILLS_DIR.exists():
        return ""

    parts = []
    for skill_dir in sorted(AGENT_SKILLS_DIR.iterdir()):
        skill_file = skill_dir / "SKILL.md"
        if skill_file.exists():
            content = skill_file.read_text(encoding="utf-8")
            # 去掉 YAML frontmatter，只保留 Markdown 正文
            if content.startswith("---"):
                # 找到第二个 --- 的位置
                end = content.find("---", 3)
                if end != -1:
                    content = content[end + 3:].strip()
            parts.append(content)

    return "\n\n---\n\n".join(parts)


def load_qa_prompt() -> str:
    """加载 QA Agent 的系统提示词"""
    path = PROMPTS_DIR / "qa_prompt.txt"
    if not path.exists():
        raise FileNotFoundError(f"QA 系统提示词文件不存在: {path}")
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# QA Agent 工厂函数
# ---------------------------------------------------------------------------

def create_qa_agent(
    workdir: str | Path,
    api_key: str | None = None,
    base_url: str | None = None,
    model_id: str | None = None,
) -> Agent:
    """
    创建 QA Agent 实例。

    Args:
        workdir: 待审查的项目工作目录
        api_key: LLM API Key（默认从环境变量读取）
        base_url: LLM API Base URL（默认从环境变量读取）
        model_id: LLM 模型 ID（默认从环境变量读取）
    """
    _api_key = api_key or os.getenv("OPENAI_API_KEY", "")
    _base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://kspmas.ksyun.com/v1")
    _model_id = model_id or os.getenv("OPENAI_MODEL", "kimi-k2.5")

    qa_prompt = load_qa_prompt()
    skills_knowledge = load_agent_skills()
    workdir = Path(workdir)

    # 将系统提示词和 Skills 知识合并为完整的 system_message
    full_system_message = qa_prompt
    if skills_knowledge:
        full_system_message += (
            "\n\n"
            "====================\n"
            "附录：专业审查知识库\n"
            "====================\n"
            "以下是你在审查时应参考的专业规则集：\n\n"
            f"{skills_knowledge}"
        )

    return Agent(
        name="QAAgent",
        model=OpenAILike(
            id=_model_id,
            api_key=_api_key,
            base_url=_base_url,
        ),
        system_message=full_system_message,
        tools=[
            FileTools(base_dir=workdir),
            ShellTools(base_dir=workdir),
        ],
        response_model=QAReport,
        markdown=True,
        debug_mode=True,
    )
