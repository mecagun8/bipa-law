# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 빌드 스펙 - BIPA 법률 AI"""

import os
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# 패키지별 숨겨진 import 수집
datas_anthropic, binaries_anthropic, hiddenimports_anthropic = collect_all("anthropic")
datas_httpx, binaries_httpx, hiddenimports_httpx = collect_all("httpx")
datas_fastapi, _, hiddenimports_fastapi = collect_all("fastapi")
datas_uvicorn, _, hiddenimports_uvicorn = collect_all("uvicorn")
datas_jinja2, _, hiddenimports_jinja2 = collect_all("jinja2")
_, _, hiddenimports_anyio = collect_all("anyio")
_, _, hiddenimports_starlette = collect_all("starlette")

a = Analysis(
    ["launcher.py"],
    pathex=["."],
    binaries=binaries_anthropic + binaries_httpx,
    datas=[
        # 앱 리소스
        ("app/templates", "templates"),
        ("app/static", "static"),
        # 패키지 데이터
        *datas_anthropic,
        *datas_httpx,
        *datas_fastapi,
        *datas_uvicorn,
        *datas_jinja2,
    ],
    hiddenimports=[
        "app.main",
        "app.claude_agent",
        "app.law_api",
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "anyio",
        "anyio._backends._asyncio",
        "email.mime.text",
        "email.mime.multipart",
        *hiddenimports_anthropic,
        *hiddenimports_httpx,
        *hiddenimports_fastapi,
        *hiddenimports_uvicorn,
        *hiddenimports_jinja2,
        *hiddenimports_anyio,
        *hiddenimports_starlette,
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy", "pandas", "PIL"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="BIPA_법률AI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,      # 콘솔창: 서버 상태 확인용 (False로 바꾸면 백그라운드 실행)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="BIPA_법률AI",
)
