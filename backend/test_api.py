#!/usr/bin/env python3
"""直接用 openai SDK 测试 API 连通性"""
import os
from dotenv import load_dotenv
load_dotenv(override=True)

from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

model = os.getenv("OPENAI_MODEL", "kimi-k2.5")

print(f"Base URL: {client.base_url}")
print(f"Model: {model}")
print(f"API Key: {client.api_key[:10]}...")
print()

# 测试 1: 非 stream
print("=== 测试 1: 非 stream ===")
try:
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "hi"}],
        max_tokens=20,
    )
    print(f"成功! 回复: {resp.choices[0].message.content}")
except Exception as e:
    print(f"失败: {type(e).__name__}: {e}")

print()

# 测试 2: stream
print("=== 测试 2: stream ===")
try:
    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "hi"}],
        max_tokens=20,
        stream=True,
    )
    content = ""
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            content += chunk.choices[0].delta.content
    print(f"成功! 回复: {content}")
except Exception as e:
    print(f"失败: {type(e).__name__}: {e}")

print()

# 测试 3: 带 system message (模拟 Agno)
print("=== 测试 3: 带 system message + stream ===")
try:
    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个网页生成助手，请用中文回复。"},
            {"role": "user", "content": "你好"},
        ],
        max_tokens=50,
        stream=True,
    )
    content = ""
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            content += chunk.choices[0].delta.content
    print(f"成功! 回复: {content}")
except Exception as e:
    print(f"失败: {type(e).__name__}: {e}")
