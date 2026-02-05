# JARVIS 시스템 매니저 (AI SysAdmin)

**Zenless Zone Zero (ZZZ)** 스타일의 HUD를 갖춘 당신만의 개인 AI 시스템 관리자입니다.
Linux 및 Windows 시스템을 실시간으로 모니터링하고, 보안 위협을 감지하며, 스스로 에러를 수정합니다.

![UI Preview](https://via.placeholder.com/800x450?text=JARVIS+HUD+Preview)

## 🚀 주요 기능

- **모니터링 월 (Monitoring Wall)**: CPU, RAM, 네트워크 속도, 보안 상태를 실시간 시각화 (CRT 감성).
- **보안 쉴드 (Security Shield)**: `apt update`, `rm -rf` 같은 위험한 명령어는 AI가 가로채서 사용자 승인을 요구합니다.
- **자가 복구 (Self-Repair)**: 시스템 에러(예: GPG 키 누락)를 감지하면 스스로 해결책(`fix_system_issue`)을 제안하고 고칩니다. (Linux 전용)
- **하이브리드 지능 (Hybrid Intelligence)**:
  - **반사 신경 (Reflex Mode)**: API 키 없이도 정해진 규칙(Regex)에 따라 빠르고 안전하게 동작합니다.
  - **두뇌 모드 (Brain Mode)**: Google Gemini API와 연동되어 복잡한 시스템 질문에도 대답합니다.

## 🛠️ 설치 방법

### 필수 조건
- **Python 3.10 이상**
- **Node.js 18 이상**
- **운영체제**: Linux (권장) 또는 Windows 10/11

### 1. 백엔드 설정 (Backend)

**Linux / macOS:**
```bash
git clone https://github.com/Start-Z-One/ai_sysadmin.git
cd ai_sysadmin

# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
pip install google-generativeai
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/Start-Z-One/ai_sysadmin.git
cd ai_sysadmin

# 가상환경 생성 및 활성화
python -m venv venv
.\venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
pip install google-generativeai
```

### 2. 프론트엔드 설정 (Frontend)
```bash
cd interface
npm install
```

### 3. API 키 설정 (Brain Mode 활성화)
AI의 추론 능력을 사용하려면 Google Gemini API 키가 필요합니다. (키가 없으면 '반사 신경' 모드로만 동작합니다.)

**Linux:**
```bash
export GEMINI_API_KEY="AIzaSy..."
```

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="AIzaSy..."
```

## ▶️ 실행 방법

두 개의 터미널이 필요합니다.

### 터미널 1: 백엔드 (The Brain)
*시스템 제어를 위해 관리자 권한이 필요합니다.*

**Linux:**
```bash
# -E 옵션: sudo 사용 시 환경변수(API Key) 유지
cd ai_sysadmin
sudo -E ./venv/bin/python main.py
```

**Windows:**
*PowerShell을 '관리자 권한'으로 실행하세요.*
```powershell
cd ai_sysadmin
.\venv\Scripts\python main.py
```

### 터미널 2: 프론트엔드 (The Face)
```bash
cd ai_sysadmin/interface
npm run dev
```

브라우저 주소창에 **http://localhost:3000** 입력.

## 🎮 사용 가이드

1. **부팅 (Boot Sequence)**: 접속 시 시스템 초기화 애니메이션과 로고가 나타납니다.
2. **명령어 예시**:
   - `sudo apt update` (Linux) / `winget upgrade --all` (Windows): 승인 요청 -> `yes` 입력 시 실행.
   - `fix error`: 시스템 로그 분석 후 자동 복구 시도.
   - `show cpu`: 상태 요약 표시.
   - (API 연동 시) "인터넷이 왜 이렇게 느려?": 현재 네트워크 상태와 프로세스를 분석해 답변.

## ⚠️ 안전 장치
`core/validator.py`에 정의된 **보안 쉴드**가 항상 작동합니다. 사용자가 명시적으로 `yes`를 입력하지 않으면 위험한 시스템 변경은 절대 실행되지 않습니다.

---
*Project "AntiGravity" - 2026*
