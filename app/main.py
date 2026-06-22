"""BIPA 법률 AI 챗봇 - FastAPI 서버"""
import json
import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .claude_agent import run_agent

load_dotenv()


def _base_dir() -> str:
    """PyInstaller 번들 또는 일반 실행 모두 대응하는 기준 경로"""
    if getattr(sys, "frozen", False):
        return sys._MEIPASS  # type: ignore[attr-defined]
    return os.path.dirname(__file__)


app = FastAPI(title="BIPA 법률 AI 어시스턴트")
_base = _base_dir()
templates = Jinja2Templates(directory=os.path.join(_base, "templates"))
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(_base, "static")),
    name="static",
)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/chat/stream")
async def chat_stream(request: Request):
    body = await request.json()
    messages = body.get("messages", [])

    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    law_key = os.getenv("LAW_API_KEY", "")

    if not anthropic_key:
        async def err():
            yield f"data: {json.dumps({'type': 'text', 'text': '⚠️ ANTHROPIC_API_KEY가 설정되지 않았습니다.'})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        return StreamingResponse(err(), media_type="text/event-stream")

    return StreamingResponse(
        run_agent(messages, anthropic_key, law_key),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
