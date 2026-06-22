#!/bin/bash
# BIPA 법률 AI - 빌드 스크립트 (macOS / Linux)
set -e

echo "=== BIPA 법률 AI 빌드 시작 ==="

pip install pyinstaller -q
pip install -r requirements.txt -q

pyinstaller bipa_law.spec --clean --noconfirm

echo ""
echo "=== 빌드 완료 ==="
echo "배포 폴더: dist/BIPA_법률AI/"
echo "실행 파일: dist/BIPA_법률AI/BIPA_법률AI"
