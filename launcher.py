"""
BIPA 법률 AI - 단독 실행 진입점
더블클릭하거나 exe로 빌드 시 이 파일이 실행됩니다.
"""
import os
import sys
import time
import threading
import webbrowser
import socket

# PyInstaller 번들 내부 경로를 모듈 탐색 경로에 추가
if getattr(sys, "frozen", False):
    bundle_dir = sys._MEIPASS  # type: ignore[attr-defined]
    sys.path.insert(0, bundle_dir)

import uvicorn
from dotenv import load_dotenv

load_dotenv()

PORT = int(os.getenv("PORT", 8000))
URL = f"http://localhost:{PORT}"


def wait_and_open_browser():
    """서버가 준비되면 브라우저 자동 오픈"""
    for _ in range(30):
        time.sleep(0.5)
        try:
            with socket.create_connection(("localhost", PORT), timeout=1):
                break
        except OSError:
            continue
    webbrowser.open(URL)


def main():
    print("=" * 50)
    print("  BIPA 법률 AI 어시스턴트")
    print(f"  서버 주소: {URL}")
    print("  종료하려면 이 창을 닫거나 Ctrl+C")
    print("=" * 50)

    # API 키 미설정 경고
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n⚠️  ANTHROPIC_API_KEY가 설정되지 않았습니다.")
        print("   실행 파일과 같은 폴더에 .env 파일을 만들고")
        print("   ANTHROPIC_API_KEY=sk-ant-... 를 입력하세요.\n")

    threading.Thread(target=wait_and_open_browser, daemon=True).start()

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=PORT,
        log_level="warning",
    )


if __name__ == "__main__":
    main()
