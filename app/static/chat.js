/* BIPA 법률 AI 채팅 클라이언트 */

const messagesEl = document.getElementById('messages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');

let conversationHistory = [];
let isStreaming = false;

// ── 초기화 ──────────────────────────────────────────
function init() {
  userInput.addEventListener('input', onInputChange);
  userInput.addEventListener('keydown', onKeyDown);
  sendBtn.addEventListener('click', submitMessage);
  document.getElementById('newChatBtn').addEventListener('click', newChat);

  document.querySelectorAll('.quick-btn').forEach(btn => {
    btn.addEventListener('click', () => submitText(btn.dataset.q));
  });
  document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => submitText(chip.dataset.q));
  });
}

// ── 입력 처리 ────────────────────────────────────────
function onInputChange() {
  userInput.style.height = 'auto';
  userInput.style.height = Math.min(userInput.scrollHeight, 160) + 'px';
  sendBtn.disabled = !userInput.value.trim() || isStreaming;
}

function onKeyDown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    if (!sendBtn.disabled) submitMessage();
  }
}

function newChat() {
  conversationHistory = [];
  messagesEl.innerHTML = `
    <div class="welcome">
      <div class="welcome-icon">⚖️</div>
      <h2>안녕하세요, BIPA 법률 AI입니다</h2>
      <p>법령 검색, 판례 조회, 법령 해석 등 법률 관련 질문을 도와드립니다.<br>궁금한 내용을 자유롭게 질문해 주세요.</p>
      <div class="welcome-chips">
        <span class="chip" data-q="근로기준법 퇴직금 지급 기준을 알려주세요.">퇴직금 규정</span>
        <span class="chip" data-q="공정거래법 위반 과징금 기준은 무엇인가요?">공정거래 과징금</span>
        <span class="chip" data-q="개인정보보호법에서 정보주체의 권리는 무엇인가요?">개인정보 권리</span>
      </div>
    </div>`;
  document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => submitText(chip.dataset.q));
  });
}

// ── 메시지 전송 ──────────────────────────────────────
function submitMessage() {
  const text = userInput.value.trim();
  if (!text || isStreaming) return;
  userInput.value = '';
  userInput.style.height = 'auto';
  sendBtn.disabled = true;
  submitText(text);
}

async function submitText(text) {
  if (isStreaming) return;

  // 환영 화면 제거
  const welcome = messagesEl.querySelector('.welcome');
  if (welcome) welcome.remove();

  // 사용자 메시지 추가
  conversationHistory.push({ role: 'user', content: text });
  appendUserMessage(text);

  // AI 답변 버블 준비
  const aiBubble = appendAiMessage('');
  isStreaming = true;
  sendBtn.disabled = true;

  let accText = '';
  let currentToolEl = null;

  try {
    const resp = await fetch('/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: conversationHistory }),
    });

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split('\n');
      buffer = lines.pop();

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        let event;
        try { event = JSON.parse(line.slice(6)); } catch { continue; }

        if (event.type === 'text') {
          accText += event.text;
          aiBubble.innerHTML = renderMarkdown(accText);
          scrollToBottom();
        } else if (event.type === 'tool_start') {
          currentToolEl = appendToolIndicator(event.tool, true);
        } else if (event.type === 'tool_end') {
          if (currentToolEl) {
            currentToolEl.querySelector('.tool-chip').classList.remove('loading');
            currentToolEl.querySelector('.tool-chip').innerHTML =
              `✅ ${toolLabel(event.tool)} 완료`;
            currentToolEl = null;
          }
        } else if (event.type === 'done') {
          break;
        }
      }
    }

    conversationHistory.push({ role: 'assistant', content: accText });
  } catch (err) {
    aiBubble.textContent = '오류가 발생했습니다: ' + err.message;
  } finally {
    isStreaming = false;
    sendBtn.disabled = !userInput.value.trim();
    scrollToBottom();
  }
}

// ── DOM 헬퍼 ────────────────────────────────────────
function appendUserMessage(text) {
  const row = document.createElement('div');
  row.className = 'msg-row user';
  row.innerHTML = `
    <div class="msg-avatar">👤</div>
    <div class="msg-bubble">${escHtml(text)}</div>`;
  messagesEl.appendChild(row);
  scrollToBottom();
}

function appendAiMessage(text) {
  const row = document.createElement('div');
  row.className = 'msg-row ai';
  row.innerHTML = `
    <div class="msg-avatar">⚖️</div>
    <div class="msg-bubble">${text}</div>`;
  messagesEl.appendChild(row);
  scrollToBottom();
  return row.querySelector('.msg-bubble');
}

function appendToolIndicator(toolName, loading) {
  const wrap = document.createElement('div');
  wrap.className = 'tool-indicator';
  wrap.innerHTML = `<span class="tool-chip ${loading ? 'loading' : ''}">🔍 ${toolLabel(toolName)} 검색 중</span>`;
  messagesEl.appendChild(wrap);
  scrollToBottom();
  return wrap;
}

function toolLabel(name) {
  const labels = {
    search_laws: '법령',
    get_law_text: '법령 본문',
    search_precedents: '판례',
    get_law_interpretation: '해석례',
  };
  return labels[name] || name;
}

function scrollToBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function escHtml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// 간단한 마크다운 렌더러
function renderMarkdown(text) {
  return escHtml(text)
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
    .replace(/^###\s+(.+)$/gm, '<strong style="font-size:15px;display:block;margin-top:10px">$1</strong>')
    .replace(/^##\s+(.+)$/gm, '<strong style="font-size:16px;display:block;margin-top:12px">$1</strong>')
    .replace(/^#\s+(.+)$/gm, '<strong style="font-size:17px;display:block;margin-top:14px">$1</strong>')
    .replace(/^[-•]\s+(.+)$/gm, '• $1')
    .replace(/\n/g, '<br>');
}

init();
