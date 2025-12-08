# Unigo - AI 기반 대학 전공 추천 챗봇

LangGraph와 RAG(Retrieval Augmented Generation)를 활용한 대학 전공 추천 및 입시 정보 제공 챗봇 시스템

## 📁 프로젝트 구조

```
frontend/
├── backend/                       # LangGraph RAG 백엔드
│   ├── data/                      # 전공 데이터 및 벡터 DB
│   │   ├── major_detail.json     # 전공 상세 정보
│   │   ├── major_categories.json # 전공 카테고리
│   │   └── vector_db/            # Pinecone 벡터 인덱스 (로컬 캐시)
│   ├── graph/                     # LangGraph 노드 및 상태
│   │   ├── nodes.py              # 전공 추천 로직, 차등 점수 시스템
│   │   ├── state.py              # 그래프 상태 정의
│   │   └── graph_builder.py      # 그래프 구성
│   ├── rag/                       # RAG 시스템
│   │   ├── retriever.py          # Pinecone 검색
│   │   ├── embeddings.py         # OpenAI 임베딩
│   │   ├── tools.py              # LangChain 툴 (전공/대학/입시 검색)
│   │   └── vectorstore.py        # 벡터 DB 연결
│   ├── main.py                    # 메인 진입점 (run_mentor, run_major_recommendation)
│   └── config.py                  # 설정 관리 (.env 로드)
│
├── unigo/                         # Django 웹 애플리케이션
│   ├── static/                    # 정적 파일
│   │   ├── css/
│   │   │   ├── styles.css        # 공통 스타일
│   │   │   └── chat.css          # 채팅 페이지 스타일
│   │   ├── js/
│   │   │   ├── script.js         # 공통 스크립트
│   │   │   └── chat.js           # 채팅 로직 (온보딩, Markdown 링크 파싱)
│   │   └── images/
│   │       └── rabbit.png        # 마스코트 이미지
│   ├── templates/                 # Django 템플릿
│   │   └── unigo_app/
│   │       ├── base.html         # 기본 레이아웃
│   │       ├── header.html       # 네비게이션
│   │       ├── home.html         # 홈 페이지
│   │       ├── chat.html         # 채팅 페이지
│   │       └── setting.html      # 설정 페이지
│   ├── unigo_app/                 # 메인 앱
│   │   ├── views.py              # API 엔드포인트 (chat_api, onboarding_api)
│   │   ├── urls.py               # URL 라우팅
│   │   └── models.py             # 데이터 모델 (현재 미사용)
│   ├── unigo/                     # 프로젝트 설정
│   │   ├── settings.py           # Django 설정
│   │   └── urls.py               # 메인 URL 설정
│   └── manage.py                  # Django 관리 스크립트
│
├── docs/                          # 프로젝트 문서
│   ├── guide.md                   # 실행 가이드
│   ├── plans.md                   # 개발 계획
│   └── fixed_log.md               # 수정 로그
│
├── assets/                        # 공통 자산
│   └── rabbit.png                # 마스코트 이미지 (원본)
│
├── .env                           # 환경 변수 (OPENAI_API_KEY 등)
├── .gitignore                     # Git 제외 파일
├── requirements.txt               # Python 의존성
└── README.md                      # 이 파일
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd frontend

# Python 가상환경 생성 (권장)
conda create -n unigo python=3.12
conda activate unigo

# 의존성 설치
pip install -r requirements.txt
pip install django
```

### 2. 환경 변수 설정

`.env.example` 파일을 `.env`로 복사하고 실제 값을 입력하세요:

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# Linux/Mac
cp .env.example .env
```

`.env` 파일을 열어 다음 항목을 설정:

```env
# ============================================
# Project Configuration
# ============================================
# 프로젝트 루트 경로 (backend 모듈 import를 위해 필요)
# ⚠️ 반드시 본인의 실제 경로로 변경하세요!
PROJECT_ROOT=C:\Users\user\github\frontend  # Windows
# PROJECT_ROOT=/home/user/github/frontend  # Linux/Mac

# ============================================
# API Keys
# ============================================
OPENAI_API_KEY=your_openai_api_key_here
LLM_PROVIDER=openai
MODEL_NAME=gpt-4o-mini
```

**중요**: `PROJECT_ROOT`는 반드시 본인의 실제 프로젝트 경로로 변경하세요!

### 3. Django 서버 실행

```bash
cd unigo
python manage.py migrate  # 최초 1회 실행
python manage.py runserver
```

### 4. 접속

브라우저에서 `http://127.0.0.1:8000/chat/` 접속

## 📚 주요 기능

## 🔑 사용자 인증 및 대화 기록 (New)
새롭게 추가된 사용자 인증 기능을 통해 대화 기록을 관리할 수 있습니다:
- **회원가입/로그인**: Username 또는 Email을 통한 간편한 계정 생성
- **대화 기록 저장**: 로그인 시 모든 대화와 전공 추천 이력이 DB에 저장됩니다.
- **세션 유지**: 비로그인 사용자는 세션 ID 기반으로 단기 기록을 유지합니다.

## 🗄️ 데이터 마이그레이션 (New)
전공 데이터(`major_detail.json`)를 DB로 적재하여 효율적인 관리가 가능합니다.

```bash
# 전공 데이터 DB 마이그레이션 실행
python manage.py load_major_data
```

## 📚 주요 기능

### 1. 온보딩 기반 전공 추천 시스템

사용자에게 4가지 질문을 통해 프로파일을 수집하고 맞춤형 전공을 추천합니다:

1. **선호 고교 과목**: 좋아하는 과목과 이유
2. **흥미 및 취미**: 학교 밖 관심사
3. **희망 연봉**: 졸업 후 목표 연봉
4. **희망 학과**: 진학하고 싶은 전공

#### 차등 점수 시스템 (Tiered Scoring)

사용자가 명시한 희망 전공에 대해 정확도에 따른 차등 점수를 부여합니다:

| 티어 | 점수 | 조건 | 예시 |
|------|------|------|------|
| Tier 1 | 20.0 | 정확히 일치 | "컴퓨터공학" == "컴퓨터공학" |
| Tier 2 | 15.0 | 접두어 일치 | "컴퓨터공학" in "컴퓨터공학**과**" |
| Tier 3 | 10.0 | 포함 | "컴퓨터" in "정보**컴퓨터**공학부" |
| Tier 4 | 5.0 | 벡터 유사도 | 의미론적으로 유사한 전공 |

### 2. RAG 기반 대화형 챗봇

**ReAct 패턴**을 활용하여 LLM이 자율적으로 필요한 정보를 검색합니다:

- **전공 정보 검색**: 관심사, 과목, 진출 분야, 연봉 정보
- **대학 검색**: 특정 전공을 개설한 대학 목록
- **입시 정보**: 대학별 정시/수시 컷 라인 (클릭 가능한 링크 제공)

#### 사용 가능한 툴 (Tools)

1. `list_departments`: 학과 목록 검색
2. `get_universities_by_department`: 학과별 개설 대학 조회
3. `get_major_career_info`: 전공별 진출 직업/분야 정보
4. `get_university_admission_info`: 대학별 입시 정보
5. `get_search_help`: 검색 도움말

### 3. Markdown 링크 지원

챗봇 응답에서 `[텍스트](URL)` 형식의 Markdown 링크를 자동으로 클릭 가능한 HTML 링크로 변환합니다.

## 🛠️ 기술 스택

### Backend
- **Python 3.10+**
- **LangChain**: LLM 오케스트레이션
- **LangGraph**: 상태 기반 에이전트 그래프
- **OpenAI GPT-4**: 언어 모델
- **Pinecone**: 벡터 데이터베이스
- **OpenAI Embeddings**: 텍스트 임베딩

### Frontend
- **Django 5.x**: 웹 프레임워크
- **HTML/CSS**: 마크업 및 스타일링
- **Vanilla JavaScript**: 클라이언트 로직 (프레임워크 없음)

### Data
- **PostgreSQL / SQLite**: 사용자, 대화 기록, 전공 데이터 저장소
- **커리어넷 & KCUE**: 원천 데이터 출처

## 📖 API 엔드포인트

### Auth API (New)
- `POST /api/auth/signup`: 회원가입
- `POST /api/auth/login`: 로그인 (Username or Email)
- `POST /api/auth/logout`: 로그아웃
- `GET /api/auth/me`: 현재 사용자 정보

### Feature API
- `POST /api/chat`: 일반 챗봇 대화 API (DB 저장 포함)
- `POST /api/onboarding`: 전공 추천 API (DB 저장 포함)

### POST `/api/chat`
**Request:**
```json
{
  "message": "컴퓨터공학과에 대해 알려줘",
  "history": [], 
  "session_id": "optional-uuid"
}
```

### POST `/api/onboarding`
**Request:**
```json
{
  "answers": {
    "subjects": "수학, 물리",
    "interests": "코딩, 게임 개발",
    "desired_salary": "5000만원",
    "preferred_majors": "컴퓨터공학과"
  }
}
```

## 🔧 개발 가이드

### 주요 파일 및 역할

#### Backend
- **`backend/graph/nodes.py`**: 전공 추천 로직 및 차등 점수 시스템
- **`backend/rag/tools.py`**: LangChain 툴 정의
- **`backend/main.py`**: `run_mentor()`, `run_major_recommendation()` 함수

#### Frontend
- **`unigo/unigo_app/views.py`**: Django API 엔드포인트
- **`unigo/static/js/chat.js`**: 채팅 UI 로직, 온보딩 플로우
- **`unigo/templates/unigo_app/chat.html`**: 채팅 페이지 템플릿

### 점수 시스템 조정

`backend/graph/nodes.py`의 상수를 수정하여 점수 시스템을 조정할 수 있습니다:

```python
# 선호 전공 점수 부여 티어
SCORE_TIER_1_EXACT_MATCH = 20.0      # 정확 일치
SCORE_TIER_2_STARTS_WITH = 15.0      # 접두어 일치
SCORE_TIER_3_CONTAINS = 10.0         # 포함
SCORE_TIER_4_VECTOR_MATCH = 5.0      # 벡터 검색

# 문서 타입별 가중치
MAJOR_DOC_WEIGHTS = {
    "summary": 1.0,
    "interest": 1.1,
    "property": 0.9,
    "subjects": 1.2,
    "jobs": 1.0,
}
```

## 📝 문서

자세한 내용은 `docs/` 폴더를 참고하세요:

- **[실행 가이드](docs/guide.md)**: 상세한 설치 및 실행 방법
- **[개발 계획](docs/plans.md)**: 프로젝트 개발 계획
- **[수정 로그](docs/fixed_log.md)**: 주요 수정 사항 기록

## 🐛 문제 해결

### Django 서버가 시작되지 않는 경우

```bash
# 마이그레이션 실행
cd unigo
python manage.py migrate

# 포트가 이미 사용 중인 경우
python manage.py runserver 8001
```

### Backend 모듈을 찾을 수 없는 경우

**방법 1 - .env 파일에서 PROJECT_ROOT 설정 (권장)**:

`.env` 파일을 열어 `PROJECT_ROOT` 설정:
```env
# Windows
PROJECT_ROOT=C:\Users\user\github\frontend

# Linux/Mac
PROJECT_ROOT=/home/user/github/frontend
```

**방법 2 - PYTHONPATH 환경 변수 설정**:
```bash
# PYTHONPATH 설정 (Windows)
set PYTHONPATH=%PYTHONPATH%;C:\path\to\frontend

# PYTHONPATH 설정 (Linux/Mac)
export PYTHONPATH=$PYTHONPATH:/path/to/frontend
```

자세한 내용은 [실행 가이드](docs/guide.md)의 "문제 해결" 섹션을 참고하세요.

### OpenAI API 오류

`.env` 파일에 올바른 API 키가 설정되어 있는지 확인하세요.

## 📄 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다.

## 👥 기여

버그 리포트 및 기능 제안은 이슈로 등록해주세요.

---

**Last Updated**: 2025-12-08