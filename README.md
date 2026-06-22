# BIPA 법률 AI 어시스턴트

내부 직원용 한국 법령 검색 AI 챗봇입니다.  
법제처 Open API + Claude AI를 활용해 법령, 판례, 해석례를 검색하고 설명합니다.

## 기능

- **법령 검색** — 법률·조례·행정규칙 검색
- **법령 본문 조회** — 특정 법령의 전문 확인
- **판례 검색** — 대법원 판례 검색
- **해석례 검색** — 법령 유권해석 검색
- **AI 답변** — Claude가 검색 결과를 바탕으로 쉽게 설명

## 실행 방법

### 1. 환경 설정

```bash
cp .env.example .env
# .env 파일에 API 키 입력
```

필요한 API 키:
- `ANTHROPIC_API_KEY` — [Anthropic Console](https://console.anthropic.com)에서 발급
- `LAW_API_KEY` — [법제처 Open API](https://open.law.go.kr)에서 무료 발급

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 서버 실행

```bash
python run.py
```

브라우저에서 `http://localhost:8000` 접속

## 주의사항

- 본 서비스는 참고용이며, 중요한 법적 판단은 전문 법률가와 상담하세요.
- 법제처 API 키 없이도 Claude AI 기본 답변은 제공됩니다.
