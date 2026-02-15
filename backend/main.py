"""
Web Builder Coding Agent - CLI 模式入口
支持两种运行方式：
  1. 交互模式: python main.py
  2. 命令行模式: python main.py <skill_id> [user_input]

v2: 使用 WebBuilderWorkflow（Developer + QA 多 Agent 协作）
"""
import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

from agents.developer import list_skills
from agents.workflow import WebBuilderWorkflow


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def run_with_skill(skill_id: str, user_input: str = ""):
    """使用 Workflow 运行完整的 生成 + QA 审查 流程"""
    print(f"\n{'='*60}")
    print(f"  Web Builder Agent v2 - Developer + QA 协作模式")
    print(f"  Skill: {skill_id}")
    print(f"{'='*60}\n")

    workflow = WebBuilderWorkflow(
        session_id=f"cli-{skill_id}",
    )

    results = list(workflow.run(skill_id=skill_id, user_input=user_input))

    if results:
        last = results[-1]
        if last.content:
            try:
                delivery = json.loads(last.content)
                print(f"\n{'='*60}")
                print(f"  生成完成！")
                print(f"  状态: {delivery.get('status', 'unknown')}")
                print(f"  项目目录: {delivery.get('workdir', 'N/A')}")
                if delivery.get("qa"):
                    qa = delivery["qa"]
                    print(f"  QA 评分: {qa.get('score', 'N/A')}/100")
                    print(f"  QA 通过: {'是' if qa.get('passed') else '否'}")
                    print(f"  问题数: {qa.get('issues_count', 0)} (critical: {qa.get('critical_count', 0)})")
                    if qa.get("fixed_files"):
                        print(f"  QA 修复: {', '.join(qa['fixed_files'])}")
                print(f"{'='*60}\n")
            except json.JSONDecodeError:
                print(last.content)
    else:
        print("[错误] Workflow 未返回结果")


def interactive_mode():
    """交互模式：选择 Skill 并输入需求"""
    print("\n" + "="*60)
    print("  Web Builder Coding Agent v2")
    print("  Developer + QA 多 Agent 协作模式")
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

    # 运行 Workflow
    run_with_skill(selected["id"], user_input)


def main():
    """入口"""
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key == "your-api-key-here":
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
