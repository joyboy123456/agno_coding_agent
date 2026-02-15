"""
Web Builder Agent - Developer Agent 定义
从原 main.py 重构提取，保持原有能力不变：
- ShellTools + FileTools 生成完整前端项目
- 加载 system_prompt.txt 作为系统提示词（宪法）
- 加载 skill YAML 模板作为差异化规格
- 执行 npm install && npm run build 自检
"""
import os
import yaml
from pathlib import Path

from agno.agent import Agent
from agno.models.openai.like import OpenAILike
from agno.tools.shell import ShellTools
from agno.tools.file import FileTools


# ---------------------------------------------------------------------------
# 路径常量
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
PROMPTS_DIR = BASE_DIR / "prompts"
SKILLS_DIR = BASE_DIR / "skills"
WORKSPACE_DIR = BASE_DIR / "workspace"

# 确保工作目录存在
WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# 公共工具函数
# ---------------------------------------------------------------------------

def load_system_prompt() -> str:
    """加载 Developer Agent 的系统提示词"""
    path = PROMPTS_DIR / "system_prompt.txt"
    if not path.exists():
        raise FileNotFoundError(f"系统提示词文件不存在: {path}")
    return path.read_text(encoding="utf-8")


def load_skill(skill_id: str) -> dict:
    """加载指定 Skill 规格"""
    path = SKILLS_DIR / f"{skill_id}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Skill 文件不存在: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def list_skills() -> list[dict]:
    """列出所有可用的 Skills"""
    skills = []
    if not SKILLS_DIR.exists():
        return skills
    for f in SKILLS_DIR.glob("*.yaml"):
        with open(f, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
            skills.append({
                "id": data.get("id", f.stem),
                "name": data.get("name", f.stem),
                "description": data.get("description", ""),
            })
    return skills


def build_user_message(skill: dict, user_input: str, run_id: str, workdir: str) -> str:
    """构建注入给 Developer Agent 的完整用户消息（按文档注入顺序）"""

    runtime_context = f"""<RUNTIME_CONTEXT>
- run_id: {run_id}
- workdir: {workdir}
- default_stack: {skill.get('stack', 'Vite + React + Tailwind CSS')}
- package_manager: npm
- build_command: npm run build
- dev_command: npm run dev
</RUNTIME_CONTEXT>"""

    skill_spec = f"""<SKILL_SPEC>
名称: {skill.get('name', '')}
描述: {skill.get('description', '')}
版本: {skill.get('version', '1.0')}
技术栈: {skill.get('stack', '')}

--- 规格模板 ---
{skill.get('prompt_template', '')}

--- 约束 ---
{yaml.dump(skill.get('constraints', []), allow_unicode=True, default_flow_style=False)}

--- 验收标准 ---
{yaml.dump(skill.get('acceptance', []), allow_unicode=True, default_flow_style=False)}
</SKILL_SPEC>"""

    user_section = f"""<USER_INPUT>
{user_input}
</USER_INPUT>"""

    return f"{runtime_context}\n\n{skill_spec}\n\n{user_section}"


# ---------------------------------------------------------------------------
# Developer Agent 工厂函数
# ---------------------------------------------------------------------------

def create_developer_agent(
    workdir: str | Path,
    api_key: str | None = None,
    base_url: str | None = None,
    model_id: str | None = None,
) -> Agent:
    """
    创建 Developer Agent 实例。

    Args:
        workdir: 项目工作目录（Agent 的文件操作限定在此目录内）
        api_key: LLM API Key（默认从环境变量读取）
        base_url: LLM API Base URL（默认从环境变量读取）
        model_id: LLM 模型 ID（默认从环境变量读取）
    """
    _api_key = api_key or os.getenv("OPENAI_API_KEY", "")
    _base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://kspmas.ksyun.com/v1")
    _model_id = model_id or os.getenv("OPENAI_MODEL", "kimi-k2.5")

    system_prompt = load_system_prompt()
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)

    return Agent(
        name="DeveloperAgent",
        model=OpenAILike(
            id=_model_id,
            api_key=_api_key,
            base_url=_base_url,
        ),
        system_message=system_prompt,
        tools=[
            ShellTools(base_dir=workdir),
            FileTools(base_dir=workdir),
        ],
        markdown=True,
        debug_mode=True,
    )
