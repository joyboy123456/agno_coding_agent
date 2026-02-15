"""
Web Builder Agent - Workflow 编排
使用 Agno Workflow 手动编排 Developer → QA 的协作流水线：
1. Developer Agent 根据 Skill 模板生成完整前端项目
2. QA Agent 审查生成的代码，输出 QAReport
3. 如果 QA 未通过且有 critical 问题，将反馈发回 Developer 修复（最多 1 轮）
4. 最终输出交付结果
"""
import json
import os
import uuid
from pathlib import Path
from typing import Iterator

from agno.agent import Agent, RunResponse
from agno.workflow import Workflow, RunEvent
from agno.utils.log import logger

from agents.developer import (
    create_developer_agent,
    load_skill,
    build_user_message,
    WORKSPACE_DIR,
)
from agents.qa import create_qa_agent
from models.schemas import QAReport


class WebBuilderWorkflow(Workflow):
    """
    Web Builder 多 Agent 协作工作流。

    流水线：Developer 生成 → QA 审查 → 条件修复 → 交付
    """

    description: str = "网页生成编程工作流：Developer 生成项目，QA 审查质量"

    # Agent 实例（延迟创建，在 run 中根据 workdir 初始化）
    developer: Agent | None = None
    qa: Agent | None = None

    def run(
        self,
        skill_id: str,
        user_input: str = "",
        run_id: str | None = None,
    ) -> Iterator[RunResponse]:
        """
        执行完整的生成 + 审查工作流。

        Args:
            skill_id: Skill 模板 ID（如 "restaurant-menu"）
            user_input: 用户补充需求
            run_id: 运行 ID（可选，默认自动生成）
        """
        # ---------------------------------------------------------------
        # 准备阶段
        # ---------------------------------------------------------------
        _run_id = run_id or uuid.uuid4().hex[:8]
        workdir = str(WORKSPACE_DIR / _run_id)
        os.makedirs(workdir, exist_ok=True)

        skill = load_skill(skill_id)

        logger.info(f"[Workflow] 开始生成 | skill={skill_id} | run_id={_run_id}")
        logger.info(f"[Workflow] 工作目录: {workdir}")

        # 创建 Agent 实例（绑定到当前 run 的工作目录）
        self.developer = create_developer_agent(workdir=workdir)
        self.qa = create_qa_agent(workdir=workdir)

        # ---------------------------------------------------------------
        # Phase 1: Developer 生成项目
        # ---------------------------------------------------------------
        logger.info("[Workflow] Phase 1: Developer 开始生成项目...")

        user_message = build_user_message(skill, user_input, _run_id, workdir)
        dev_response: RunResponse = self.developer.run(user_message)

        if not dev_response or not dev_response.content:
            logger.error("[Workflow] Developer Agent 未返回有效内容")
            yield RunResponse(
                event=RunEvent.workflow_completed,
                content=json.dumps({
                    "run_id": _run_id,
                    "status": "fail",
                    "error": "Developer Agent 未返回有效内容",
                }, ensure_ascii=False),
            )
            return

        logger.info("[Workflow] Phase 1 完成: Developer 已生成项目")

        # ---------------------------------------------------------------
        # Phase 2: QA 审查
        # ---------------------------------------------------------------
        logger.info("[Workflow] Phase 2: QA 开始审查...")

        qa_input = (
            f"请审查以下项目目录中的所有代码文件:\n"
            f"项目目录: {workdir}\n"
            f"技术栈: {skill.get('stack', 'Vite + React + Tailwind CSS')}\n"
            f"项目类型: {skill.get('name', '未知')}\n\n"
            f"请按照你的审查流程，逐维度检查并输出 QAReport。"
        )

        qa_response: RunResponse = self.qa.run(qa_input)

        # 解析 QA 报告
        qa_report: QAReport | None = None
        if qa_response and qa_response.content:
            if isinstance(qa_response.content, QAReport):
                qa_report = qa_response.content
            else:
                # 尝试从字符串解析
                try:
                    qa_report = QAReport.model_validate_json(
                        qa_response.content
                        if isinstance(qa_response.content, str)
                        else json.dumps(qa_response.content)
                    )
                except Exception as e:
                    logger.warning(f"[Workflow] QA 报告解析失败: {e}")

        if not qa_report:
            logger.warning("[Workflow] QA Agent 未返回有效报告，跳过审查环节")
            yield RunResponse(
                event=RunEvent.workflow_completed,
                content=self._build_delivery_json(
                    _run_id, workdir, skill, qa_report=None
                ),
            )
            return

        logger.info(
            f"[Workflow] Phase 2 完成: QA 评分={qa_report.score}, "
            f"通过={qa_report.passed}, "
            f"问题数={len(qa_report.issues)}"
        )

        # ---------------------------------------------------------------
        # Phase 3: 条件修复（仅当 QA 未通过时）
        # ---------------------------------------------------------------
        if not qa_report.passed and qa_report.score < 80:
            critical_issues = [
                i for i in qa_report.issues if i.severity == "critical"
            ]

            if critical_issues:
                logger.info(
                    f"[Workflow] Phase 3: 发现 {len(critical_issues)} 个 critical 问题，"
                    f"发回 Developer 修复..."
                )

                fix_message = (
                    "QA 审查发现以下 critical 问题，请逐一修复：\n\n"
                    + "\n".join(
                        f"- [{i.category}] {i.file_path}: {i.description}\n"
                        f"  建议: {i.suggestion}"
                        for i in critical_issues
                    )
                    + "\n\n修复完成后，请重新执行 npm run build 确认构建通过。"
                )

                self.developer.run(fix_message)
                logger.info("[Workflow] Phase 3 完成: Developer 已尝试修复")
            else:
                logger.info("[Workflow] Phase 3 跳过: 无 critical 问题需要修复")

        # ---------------------------------------------------------------
        # Phase 4: 交付
        # ---------------------------------------------------------------
        logger.info("[Workflow] Phase 4: 生成交付结果")

        yield RunResponse(
            event=RunEvent.workflow_completed,
            content=self._build_delivery_json(
                _run_id, workdir, skill, qa_report
            ),
        )

    @staticmethod
    def _build_delivery_json(
        run_id: str,
        workdir: str,
        skill: dict,
        qa_report: QAReport | None,
    ) -> str:
        """构建最终交付 JSON"""
        delivery = {
            "run_id": run_id,
            "status": "success",
            "workdir": workdir,
            "skill": skill.get("name", ""),
            "stack": skill.get("stack", ""),
            "qa": None,
        }

        if qa_report:
            delivery["qa"] = {
                "passed": qa_report.passed,
                "score": qa_report.score,
                "summary": qa_report.summary,
                "issues_count": len(qa_report.issues),
                "critical_count": len(
                    [i for i in qa_report.issues if i.severity == "critical"]
                ),
                "fixed_files": qa_report.fixed_files,
            }

        return json.dumps(delivery, ensure_ascii=False, indent=2)
