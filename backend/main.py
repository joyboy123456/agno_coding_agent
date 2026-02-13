"""
Web Builder Coding Agent - 最小可验证原型 (PoC)
基于 Agno 框架，使用 OpenAI 兼容接口 (金山云 kimi-k2.5)
"""
import os
import sys
import uuid
import yaml
from pathlib import Path
from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.openai.like import OpenAILike
from agno.tools.shell import ShellTools
from agno.tools.file import FileTools

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY", "")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://kspmas.ksyun.com/v1")
MODEL_ID = os.getenv("OPENAI_MODEL", "kimi-k2.5")

BASE_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = BASE_DIR / "prompts"
SKILLS_DIR = BASE_DIR / "skills"
WORKSPACE_DIR = BASE_DIR / "workspace"

# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def load_system_prompt() -> str:
    """加载系统提示词"""
    path = PROMPTS_DIR / "system_prompt.txt"
    if not path.exists():
        print(f"[错误] 系统提示词文件不存在: {path}")
        sys.exit(1)
    return path.read_text(encoding="utf-8")


def load_skill(skill_id: str) -> dict:
    """加载 Skill 规格"""
    path = SKILLS_DIR / f"{skill_id}.yaml"
    if not path.exists():
        print(f"[错误] Skill 文件不存在: {path}")
        sys.exit(1)
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
    """构建注入给 Agent 的完整用户消息（按文档注入顺序）"""

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


def create_agent(system_prompt: str, workdir: str) -> Agent:
    """创建 Web Builder Agent"""
    return Agent(
        name="WebBuilderAgent",
        model=OpenAILike(
            id=MODEL_ID,
            api_key=API_KEY,
            base_url=BASE_URL,
        ),
        system_message=system_prompt,
        tools=[
            ShellTools(base_dir=Path(workdir)),
            FileTools(base_dir=Path(workdir)),
        ],
        markdown=True,
        debug_mode=True,
    )


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def run_with_skill(skill_id: str, user_input: str = ""):
    """使用指定 Skill 运行 Agent"""
    # 1. 加载
    skill = load_skill(skill_id)
    system_prompt = load_system_prompt()
    run_id = uuid.uuid4().hex[:8]
    workdir = str(WORKSPACE_DIR / run_id)

    # 2. 创建工作目录
    os.makedirs(workdir, exist_ok=True)
    print(f"\n{'='*60}")
    print(f"  Web Builder Agent - 开始生成")
    print(f"  Skill: {skill.get('name', skill_id)}")
    print(f"  Run ID: {run_id}")
    print(f"  工作目录: {workdir}")
    print(f"{'='*60}\n")

    # 3. 构建消息并运行
    agent = create_agent(system_prompt, workdir)
    user_message = build_user_message(skill, user_input, run_id, workdir)
    agent.print_response(user_message, stream=True)

    print(f"\n{'='*60}")
    print(f"  生成完成！")
    print(f"  项目目录: {workdir}")
    print(f"{'='*60}\n")


def interactive_mode():
    """交互模式：选择 Skill 并输入需求"""
    print("\n" + "="*60)
    print("  Web Builder Coding Agent (PoC)")
    print("  基于 Agno + kimi-k2.5")
    print("="*60)

    # 列出可用 Skills
    skills = list_skills()
    if not skills:
        print("\n[错误] 没有找到任何 Skill 文件，请检查 skills/ 目录")
        sys.exit(1)

    print("\n可用模板：")
    for i, s in enumerate(skills, 1):
        print(f"  {i}. {s['name']} - {s['description']}")

    # 选择 Skill
    while True:
        try:
            choice = input(f"\n请选择模板 (1-{len(skills)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(skills):
                selected = skills[idx]
                break
            print("无效选择，请重试")
        except (ValueError, KeyboardInterrupt):
            print("\n再见！")
            sys.exit(0)

    # 用户补充需求
    print(f"\n已选择: {selected['name']}")
    user_input = input("请输入补充需求（可直接回车跳过）: ").strip()

    # 运行
    run_with_skill(selected["id"], user_input)


def main():
    """入口"""
    if not API_KEY or API_KEY == "your-api-key-here":
        print("[错误] 请先配置 OPENAI_API_KEY")
        print("  1. 复制 .env.example 为 .env")
        print("  2. 填入你的 API Key")
        sys.exit(1)

    if len(sys.argv) > 1:
        # 命令行模式: python main.py <skill_id> [user_input]
        skill_id = sys.argv[1]
        user_input = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        run_with_skill(skill_id, user_input)
    else:
        # 交互模式
        interactive_mode()


if __name__ == "__main__":
    main()
