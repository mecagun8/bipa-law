"""Claude API + 법제처 tool use 에이전트"""
import json
import os
from typing import AsyncGenerator

import anthropic

from .law_api import get_law_interpretation, get_law_text, search_laws, search_precedents

LAW_TOOLS = [
    {
        "name": "search_laws",
        "description": (
            "법령 제목 또는 키워드로 법령을 검색합니다. "
            "law_type: 'law'(법률), 'ordinance'(조례), 'regulation'(행정규칙)"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "검색어 (법령명 또는 키워드)"},
                "law_type": {
                    "type": "string",
                    "enum": ["law", "ordinance", "regulation"],
                    "description": "법령 종류",
                },
                "count": {"type": "integer", "description": "결과 수 (기본 5)", "default": 5},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_law_text",
        "description": "법령 ID 또는 법령명으로 법령 본문을 가져옵니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "law_id": {"type": "string", "description": "법령 ID 또는 법령명"},
            },
            "required": ["law_id"],
        },
    },
    {
        "name": "search_precedents",
        "description": "키워드로 판례를 검색합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "검색어"},
                "count": {"type": "integer", "description": "결과 수 (기본 5)", "default": 5},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_law_interpretation",
        "description": "법령 해석례(유권해석)를 검색합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "검색어"},
            },
            "required": ["query"],
        },
    },
]

SYSTEM_PROMPT = """당신은 비파(BIPA) 법률 AI 어시스턴트입니다. 내부 직원들의 법령 관련 질문에 답변합니다.

역할:
- 법령 검색 및 조문 안내
- 판례 및 법령 해석례 검색
- 법령의 내용을 쉽게 설명
- 실무에 필요한 법적 근거 제시

주의사항:
- 제공하는 정보는 참고용이며, 중요한 법적 판단은 전문 법률가와 상담하세요.
- 항상 출처(법령명, 조항)를 명시하세요.
- 한국어로 명확하고 간결하게 답변하세요.
- 법제처 데이터를 기반으로 정확한 정보를 제공하세요."""


async def run_agent(
    messages: list[dict],
    anthropic_key: str,
    law_key: str,
) -> AsyncGenerator[str, None]:
    """스트리밍 에이전트 실행 - SSE 포맷으로 yield"""
    client = anthropic.Anthropic(api_key=anthropic_key)

    current_messages = list(messages)

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=LAW_TOOLS,
            messages=current_messages,
        )

        # 텍스트 블록 스트리밍
        for block in response.content:
            if block.type == "text":
                yield f"data: {json.dumps({'type': 'text', 'text': block.text})}\n\n"

        if response.stop_reason == "end_turn":
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            break

        if response.stop_reason != "tool_use":
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            break

        # tool use 처리
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            yield f"data: {json.dumps({'type': 'tool_start', 'tool': block.name, 'input': block.input})}\n\n"

            try:
                result = await _call_tool(block.name, block.input, law_key)
            except Exception as e:
                result = {"error": str(e)}

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(result, ensure_ascii=False),
            })

            yield f"data: {json.dumps({'type': 'tool_end', 'tool': block.name})}\n\n"

        current_messages = current_messages + [
            {"role": "assistant", "content": response.content},
            {"role": "user", "content": tool_results},
        ]


async def _call_tool(name: str, inputs: dict, law_key: str) -> dict:
    if name == "search_laws":
        return await search_laws(
            query=inputs["query"],
            api_key=law_key,
            count=inputs.get("count", 5),
            law_type=inputs.get("law_type", "law"),
        )
    elif name == "get_law_text":
        return await get_law_text(law_id=inputs["law_id"], api_key=law_key)
    elif name == "search_precedents":
        return await search_precedents(
            query=inputs["query"],
            api_key=law_key,
            count=inputs.get("count", 5),
        )
    elif name == "get_law_interpretation":
        return await get_law_interpretation(query=inputs["query"], api_key=law_key)
    else:
        return {"error": f"알 수 없는 도구: {name}"}
