# Unigo - AI 기반 대학 전공 추천 챗봇

LangGraph와 RAG(Retrieval Augmented Generation)를 활용한 대학 전공 추천 및 입시 정보 제공 챗봇 시스템입니다.

## 📁 프로젝트 구조

```
Unigo/
├── backend/                       # LangGraph RAG 백엔드
│   ├── data/                      # 전공 데이터 (MySQL 시딩용)
│   │   ├── major_detail.json      # 전공 상세 정보 원본
│   │   ├── major_categories.json  # 전공 카테고리
│   │   └── university_data_cleaned.json # 대학 정보
│   ├── db/                        # 데이터베이스 관리 (SQLAlchemy)
│   │   ├── connection.py          # DB 연결 설정
│   │   ├── models.py              # DB 모델 정의 (Major, University 등)
│   │   ├── seed_all.py            # 통합 데이터 시딩 스크립트
│   │   └── seed_*.py              # 개별 시딩 스크립트
│   ├── graph/                     # LangGraph 노드 및 상태
│   │   ├── nodes.py               # 전공 추천 로직, 차등 점수 시스템
│   │   ├── state.py               # 그래프 상태 정의
│   │   └── graph_builder.py       # 그래프 구성
│   ├── rag/                       # RAG 시스템
│   │   ├── retriever.py           # Pinecone 검색 로직
│   │   ├── embeddings.py          # OpenAI 임베딩 핸들러
│   │   ├── tools.py               # LangChain 툴 (전공/대학/입시 검색)
│   │   ├── vectorstore.py         # Pinecone 벡터 DB 연결 및 인덱싱
│   │   ├── loader.py              # 데이터 로딩 유틸리티
│   │   └── build_major_index.py   # 전공 상세 정보 벡터 인덱싱 스크립트
│   ├── scripts/                   # 추가 유틸리티 스크립트
│   │   ├── ingest_major_categories.py   # 학과 대분류 벡터 인덱싱
│   │   └── ingest_university_majors.py  # 대학별 학과 정보 벡터 인덱싱
│   ├── main.py                    # 메인 진입점 (run_mentor, run_major_recommendation)
│   └── config.py                  # 설정 관리 (.env 로드)
│
├── unigo/                         # Django 웹 애플리케이션
│   ├── static/                    # 정적 파일 (CSS, JS, Images)
│   │   ├── css/                   # 스타일시트
│   │   ├── js/                    # 클라이언트 로직 (chat.js 등)
│   │   └── images/                # 이미지 자산
│   ├── templates/                 # Django HTML 템플릿
│   ├── unigo_app/                 # 메인 Django 앱
│   │   ├── views.py               # API 엔드포인트 및 뷰
│   │   ├── urls.py                # URL 라우팅
│   │   └── models.py              # Django 모델 (UserProfile, Conversation 등)
│   ├── unigo/                     # Django 프로젝트 설정
│   └── manage.py                  # Django 관리 스크립트
│
├── docs/                          # 프로젝트 문서
├── assets/                        # 공통 자산
├── .env                           # 환경 변수 (OPENAI_API_KEY 등)
├── .gitignore                     # Git 제외 파일
└── requirements.txt               # Python 의존성
```

## 🚀 빠른 시작 (Quick Start)

### 1. 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd Unigo

# Python 가상환경 생성 (Python 3.10 이상 권장)
conda create -n unigo python=3.11
conda activate unigo

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env.example` 파일을 `.env`로 복사하고 실제 값을 입력하세요:

```bash
cp .env.example .env
```

`.env` 파일 필수 설정 항목:

```env
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENV=your_pinecone_environment

# Database (MySQL)
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=unigo

# Django Secret
DJANGO_SECRET_KEY=your_django_secret_key
```

### 3. 데이터베이스 구축 (MySQL & Pinecone)

이 프로젝트는 **MySQL**(정형 데이터)과 **Pinecone**(벡터 데이터)을 모두 사용합니다.

#### 1) MySQL 설정 및 데이터 시딩

웹 애플리케이션과 RAG 검색을 위한 기초 데이터를 MySQL에 적재합니다.

```bash
# 1. Django 마이그레이션 (테이블 생성)
python unigo/manage.py makemigrations
python unigo/manage.py migrate

# 2. 초기 데이터 통합 시딩 (전공, 카테고리, 대학, 입시 URL 정보)
python -m backend.db.seed_all
```

#### 2) Pinecone 벡터 인덱싱

RAG 검색 정확도를 높이기 위해 3가지 네임스페이스에 데이터를 인덱싱합니다.

```bash
# 1. 전공 상세 정보 인덱싱 (Namespace: majors)
#    - 전공 요약, 흥미, 특성, 진로, 관련 과목 등을 벡터화
python -m backend.rag.build_major_index

# 2. 학과 대분류 인덱싱 (Namespace: major_categories)
#    - 검색어 확장 및 의미 기반 학과 분류 검색용
python -m backend.scripts.ingest_major_categories

# 3. 대학별 학과 정보 인덱싱 (Namespace: university_majors)
#    - 특정 대학의 특정 학과 존재 여부 및 상세 매칭용
python -m backend.scripts.ingest_university_majors
```

### 4. 서버 실행

```bash
cd unigo
python manage.py runserver
```

브라우저에서 `http://127.0.0.1:8000/` 접속하여 서비스를 시작하세요.

---

## 📚 주요 기능

### 1. 🤖 RAG 기반 AI 멘토

**ReAct(Reasoning + Acting) 패턴**을 적용한 AI 에이전트가 사용자의 질문을 분석하고 필요한 정보를 실시간으로 검색하여 답변합니다.

- **전공 탐색**: "인공지능 배우려면 무슨 과 가야 해?" -> 관련 학과 및 커리큘럼 소개
- **대학 검색**: "컴퓨터공학과 있는 서울 대학 어디야?" -> 개설 대학 목록 및 위치 정보 제공
- **진로 상담**: "기계공학과 나오면 취업 잘 돼?" -> 취업률, 평균 연봉, 주요 진출 분야(커리어넷 데이터 기준) 제공
- **입시 정보**: 각 대학 입학처의 수시/정시 모집요강 바로가기 링크 제공

#### 🧠 LangGraph Workflow (에이전트 구조)

AI 멘토는 **LangGraph**를 사용하여 상태 기반의 워크플로우를 관리합니다.

1.  **ReAct Agent Graph**:
    ```mermaid
    graph LR
    Start --> Agent
    Agent -- 도구 호출 --> Tools
    Tools -- 결과 반환 --> Agent
    Agent -- 답변 생성 --> End
    ```
    - **Agent 노드**: 사용자의 질문을 분석하고 도구(Tool) 사용 여부를 결정합니다.
    - **Tools 노드**: 벡터 DB 검색(Pinecone), 대학 정보 조회 등 실제 작업을 수행합니다.
    - **순환 구조(Loop)**: 에이전트는 필요한 정보를 모두 얻을 때까지 `Agent ↔ Tools` 과정을 반복할 수 있습니다.

2.  **Major Recommendation Graph**:
    - **Recommend 노드**: 온보딩 데이터를 입력받아 [프로필 분석 -> 벡터 검색 -> 점수 산출] 과정을 단방향 파이프라인으로 수행합니다.

### 2. 🎓 맞춤형 전공 추천 (온보딩)

사용자와의 초기 인터뷰(7가지 질문)를 통해 성향을 분석하고 최적의 전공을 추천합니다.

- **분석 요소**: 선호 과목, 관심사, 활동 유형, 선호 환경, 가치관, 관심 주제, 학습 스타일
- **알고리즘**: 사용자 프로필 벡터와 전공 특성 벡터 간의 다차원 유사도 분석 + 가중치 적용 점수 시스템

### 3. 🔑 사용자 경험 (UX)

- **회원가입/로그인**: 개인화된 대화 기록 및 추천 결과 저장
- **채팅 히스토리**: 이전 상담 내용을 언제든지 다시 확인 가능
- **마크다운 지원**: 가독성 높은 텍스트 및 클릭 가능한 링크 제공
- **페르소나 캐릭터**: 친근한 캐릭터(토끼 등) 기반 인터페이스

## 🛠️ 기술 스택

| 분류 | 기술 | 비고 |
|------|------|------|
| **Backend** | Python 3.10+, Django 5.x | 웹 프레임워크 및 API |
| **Data** | MySQL, SQLAlchemy | 관계형 데이터베이스 (전공/대학 정보, 사용자 데이터) |
| **AI / RAG** | LangChain, LangGraph | AI 에이전트 및 워크플로우 관리 |
| **LLM** | OpenAI GPT-4o | 추론 및 자연어 생성 |
| **Vector DB** | Pinecone | 고성능 벡터 검색 |
| **Frontend** | HTML5, CSS3, Vanilla JS | 반응형 웹 인터페이스 |

## 📖 API 엔드포인트

### 인증 (Auth)

- `POST /api/auth/signup`: 회원가입
- `POST /api/auth/login`: 로그인
- `GET /api/auth/me`: 내 정보 조회

### 기능 (Features)

- `POST /api/chat`: 챗봇 대화 (RAG 엔진 연동)
- `POST /api/onboarding`: 전공 추천 (온보딩 결과 분석)
- `GET /api/chat/history`: 대화 기록 조회

## 🧪 테스트 및 검증

로컬 환경에서 LLM 로직을 테스트하려면 `test_llm.py`(존재 시) 또는 개별 모듈 단위 테스트를 수행할 수 있습니다.
(현재 `backend/main.py`를 직접 실행하여 CLI 모드로 테스트 가능)

```bash
# CLI 모드 테스트
python -m backend.main
```

## 📄 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다.
