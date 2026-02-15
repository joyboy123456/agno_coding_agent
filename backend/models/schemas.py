"""
Web Builder Agent - 数据模型定义
QA Agent 的结构化输出模型
"""
from pydantic import BaseModel, Field


class QAIssue(BaseModel):
    """单个审查问题"""
    severity: str = Field(
        ...,
        description="问题严重程度: critical / warning / info",
    )
    category: str = Field(
        ...,
        description="问题分类: react-practices / ui-ux / performance / accessibility",
    )
    file_path: str = Field(
        ...,
        description="问题所在文件的相对路径",
    )
    description: str = Field(
        ...,
        description="问题的具体描述",
    )
    suggestion: str = Field(
        ...,
        description="修复建议",
    )


class QAReport(BaseModel):
    """QA Agent 的审查报告"""
    passed: bool = Field(
        ...,
        description="是否通过审查（无 critical 问题且综合评分 >= 80）",
    )
    score: int = Field(
        ...,
        description="综合评分 0-100",
    )
    summary: str = Field(
        ...,
        description="审查摘要，一段话概括整体质量",
    )
    issues: list[QAIssue] = Field(
        default_factory=list,
        description="发现的问题列表",
    )
    fixed_files: list[str] = Field(
        default_factory=list,
        description="QA 直接修复的文件路径列表",
    )
