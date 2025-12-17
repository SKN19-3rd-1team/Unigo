# SK네트웍스 Family AI 캠프 19기 4차 프로젝트

## 1. 팀 소개

### 팀명
**Unigo (유니고)** - University Go, 당신을 위한 대학 입시 가이드

### 멤버
<div align="center">
  <table>
  <tr>
    <td align="center"> 
			<img src="unigo/static/images/raccoon.png" width="200" alt="강지완">     
			 <br/>
      강지완
      <br/>
      <a href="https://github.com/Maroco0109">
        <img src="https://img.shields.io/badge/GitHub-Maroco0109-181717?style=flat&logo=github&logoColor=white">
      </a>
    </td> 
    <td align="center"> 
			<img src="unigo/static/images/penguin.png" width="200" alt="김진">       
			<br/>
      김진
      <br/>
      <a href="https://github.com/KIMjjjjjjjj">
        <img src="https://img.shields.io/badge/GitHub-KIMjjjjjjjj-181717?style=flat&logo=github&logoColor=white">
      </a>
    </td>
    <td align="center"> 
				<img src="unigo/static/images/turtle.png" width="200" alt="마한성">       
			<br/>
      마한성
      <br/>
      <a href="https://github.com/gitsgetit">
        <img src="https://img.shields.io/badge/GitHub-gitsgetit-181717?style=flat&logo=github&logoColor=white">
      </a>
    </td> 
    <td align="center"> 
			<img src="unigo/static/images/bear.png" width="200" alt="오하원">      
			<br/> 
      오하원
      <br/>
      <a href="https://github.com/Hawon-Oh">
        <img src="https://img.shields.io/badge/GitHub-Hawon--Oh-181717?style=flat&logo=github&logoColor=white">
      </a>
    </td> 
  </tr>
</table>
</div>

---

## 2. 프로젝트 변경 사항

> **"단순 정보 검색에서 개인화된 입시 멘토링 서비스로"**
>
> 이전 3차 프로젝트(공신2)의 한계를 분석하고, 기술적/기능적으로 대폭 개선했습니다.

### 주요 개선 포인트

| 구분 | 3차 프로젝트 (공신2) | **4차 프로젝트 (Unigo)** | 비고 |
| :--- | :--- | :--- | :--- |
| **타겟/범위** | 16개 대학 커리큘럼 중심 (제한적) | **전국 대학 및 전체 전공 데이터** (확장) | 입시생 전체로 타겟 확장 |
| **데이터 원천** | 대학별 크롤링 (비정형 데이터) | **공공 데이터 API & MySQL** (정제된 데이터) | 데이터 신뢰성 및 관리 효율 증대 |
| **핵심 기술** | **ReAct Agent & LangGraph** (추론형 AI) | **ReAct Agent & LangGraph** (추론형 AI) | 일부 tool 변경 |
| **플랫폼** | Streamlit (프로토타입) | **Django Web Application** (상용화 수준) | 회원가입, 커스텀 UI/UX 구현 가능 |
| **UX 전략** | 기능 중심 Q&A | **페르소나(캐릭터) & 온보딩** | 사용자 몰입감 및 친밀도 향상 |


### 개선 배경 및 원인

#### 초기 데이터 수집의 한계

- **크롤링 난이도**: 대학마다 상이한 홈페이지 양식과 보안(봇 탐지) 이슈로 인해 안정적인 데이터 수집이 어려움.
- **데이터 파편화**: 학과명이 대학별로 제각각(예: 컴퓨터공학과, SW학부, AI전공...)이라 정규화 및 매핑이 매우 난해함.
- **커리큘럼의 모호성**: 명확한 커리큘럼이 온라인에 공개되지 않은 대학이 많아 일관된 정보 제공 불가.

#### 사용자 경험(UX) 저하

- **제한된 커버리지**: 서울 주요 대학이나 이공계열 위주로 정보가 편중되어, 실제 사용자가 찾는 지방 대학이나 인문/예체능 계열 정보 누락.
- **검색 실패**: 사용자가 원하는 결과가 없음(No Result)으로 나오는 빈도가 높아 서비스 만족도 하락.

<br>

### 데이터 및 시스템 고도화

#### 데이터 소스 변경 (신뢰성 확보)

기존의 불안정한 크롤링 방식을 버리고, **공공 데이터 API**를 도입하여 데이터의 완결성을 확보했습니다.

| 구분          | 소스                                          | 설명                                            |
| :------------ | :-------------------------------------------- | :---------------------------------------------- |
| **학과 정보** | [커리어넷 API](https://www.career.go.kr/)     | 표준 학과명, 진로, 직업, 자격증 등 메타 데이터  |
| **입시/대학** | [대입정보포털 (Adiga)](https://www.adiga.kr/) | 2025학년도 최신 입시 요강, 개설 학과, 대학 코드 |

#### 주요 기대 효과

1.  **데이터 커버리지 100%**: 국내 존재하는 모든 대학 및 학과 정보 탑재.
2.  **정교한 검색 경험**:
    - **정확한 학과 검색**: "연세대학교에 컴퓨터 공학과가 있어?" → "연세대학교에는 "컴퓨터공학과"라는 명칭의 학과는 없지만, "인공지능학과"와 "첨단컴퓨팅학부"가 개설되어 있습니다. 이 두 학과는 컴퓨터 관련 분야와 밀접한 연관이 있습니다."
3.  **One-Stop 입시 정보**: 단순 학과 소개를 넘어, 해당 학과가 개설된 대학 리스트와 입시처 링크까지 연결.

#### 핵심 기능 (Tools) 구현

| 기능(Tool)                       | 설명                             | 기술 스택                                          |
| :------------------------------- | :------------------------------- | :------------------------------------------------- |
| `list_departments`               | 키워드/카테고리 기반 학과 추천   | **Pinecone** (Vector) + **MySQL**                  |
| `get_universities_by_department` | 특정 전공 개설 대학 및 학과 매칭 | **Pinecone** + **MySQL** |
| `get_major_career_info`          | 진로, 연봉, 취업률 등 상세 정보  | **MySQL** (CareerNet Data)                         |
| `get_university_admission_info`  | 대학별 입시 요강 페이지 연결     | **MySQL** (Adiga Data)                             |

<br>

### 데이터 및 전처리 과정

#### 데이터 소스 (Data Sources)
- **major_detail.json(커리어넷)**: 전공 상세 정보 (학과명, 요약, 흥미, 적성, 진출 분야, 관련 직업, 관련 자격증, 주요 교과목, 졸업 후 연봉, 취업률, 입학 경쟁률, 개설 대학 목록 등)
- **university_data_cleaned.json(대학어디가)**: 대학별 정보 및 주소
- **major_categories.json(커리어넷)**: 대분류 학과와 그에 해당하는 학과들 나열

#### 전처리 파이프라인 (Processing Pipeline)
1. **Data Ingestion (데이터 수집 및 로드)**
   - 커리어넷 등에서 수집된 대용량 JSON 파일 로드 및 원본 데이터의 복잡한 중첩 구조(`dataSearch > content`) 파싱
2. **Dual-Store Strategy (이원화 저장 전략)**
   - **MySQL (Structured Data)**: 전공명, 취업률, 연봉 등 정형 데이터를 RDBMS 테이블 스키마에 맞춰 매핑 및 적재
   - **Pinecone (Vector Data)**: 자연어 검색을 위해 전공 개요, 흥미, 적성 등 텍스트 데이터를 `MajorDoc` 문서 객체로 변환하여 임베딩 및 인덱싱
3. **Optimization (인덱싱 최적화)**
   - 데이터 특성에 따라 3가지 네임스페이스(`majors`, `major_categories`, `university_majors`)로 분리하여 벡터화 수행

### 인프라 전환: Vector DB (Migration)

> **Chroma DB (Local)** ➡️ **Pinecone (Serverless Cloud)**

#### 전환 이유

1.  **운영 복잡도 해소**: 로컬 DB 관리(Docker Volume, 파일 손상 등)의 부담을 덜고 완전 관리형(SaaS) 서비스 도입.
2.  **Serverless 효율**: 트래픽이 없을 땐 비용이 0에 수렴하며, 필요시 즉각 스케일링되는 유연한 구조.

#### 도입 효과

- **Stateless 아키텍처**: 백엔드 컨테이너를 언제든 껐다 켜도 데이터 동기화 문제 없음 (Docker Compose 구성 단순화).
- **개발 편의성**: 팀원 간 로컬 환경(OS, 디스크 경로 등) 차이 없이 동일한 API 키로 동일한 검색 결과 보장.

---

## 3. 프로젝트 개요

### 프로젝트 명
**Unigo (AI 기반 대학 전공 추천 및 입시 상담 챗봇)**

### 프로젝트 소개
LLM(Large Language Model)과 RAG(Retrieval Augmented Generation) 기술을 활용하여 수험생과 진로를 고민하는 학생들에게 **개인 맞춤형 전공 추천**과 **정확한 입시 정보**를 제공하는 대화형 AI 서비스입니다.

### 프로젝트 필요성 (배경)
- **정보의 비대칭성**: 대학 입시 정보는 **방대하고 파편화**되어 있어 학생들이 자신에게 맞는 정보를 찾기 어렵습니다.
- **맞춤형 상담의 부재**: 기존의 커리어넷/워크넷 등은 정적인 정보만 제공하며, **개인의 성향을 고려한 심층적인 대화형 상담이 부족합니다**.
- **비용 문제**: 사설 입시 컨설팅은 **고비용**으로 접근성이 낮습니다. 누구나 쉽게 접근 가능한 AI 멘토가 필요합니다.

### 프로젝트 목표
1. **정확성**: Pinecone 벡터 DB와 RAG를 통해 Hallucination을 최소화한 신뢰성 있는 정보 제공
2. **개인화**: LangGraph 기반의 ReAct 에이전트를 통해 사용자의 의도를 파악하고 다단계 추론을 통한 맞춤 답변 제공
3. **편의성**: 직관적인 채팅 인터페이스와 사용자 친화적인 온보딩 프로세스 구축

---

## 4. 프로젝트 구조

```
Unigo/
├── backend/                             # AI 백엔드 (LangGraph + RAG)
│   ├── data/                            # 초기 데이터 (Seeding)
│   │   ├── major_detail.json            # 학과 상세 정보 (커리어넷)
│   │   ├── major_categories.json        # 학과 대분류 데이터
│   │   └── university_data_cleaned.json # 대학 기본 정보 (대학어디가)
│   ├── db/                              # DB 관리 (SQLAlchemy)
│   │   ├── connection.py                # DB 연결 설정
│   │   ├── models.py                    # DB 테이블 모델 (Major, University 등)
│   │   ├── seed_all.py                  # 전체 데이터 시딩 실행
│   │   └── seed_*.py                    # 개별 테이블 시딩 스크립트
│   ├── graph/                           # LangGraph 워크플로우
│   │   ├── graph_builder.py             # 그래프 구조 및 엣지 연결
│   │   ├── nodes.py                     # 노드별 로직 (Agent, Tools)
│   │   ├── state.py                     # 그래프 상태(State) 정의
│   │   └── helper.py                    # 그래프 유틸리티
│   ├── rag/                             # RAG 시스템
│   │   ├── tools.py                     # LangChain 도구 (검색, 조회)
│   │   ├── retriever.py                 # Pinecone 검색 로직
│   │   ├── embeddings.py                # 임베딩 생성 (OpenAI)
│   │   ├── vectorstore.py               # Pinecone 클라이언트 및 인덱싱
│   │   ├── loader.py                    # JSON 데이터 로딩 및 파싱
│   │   └── build_major_index.py         # 벡터 인덱스 생성 스크립트
│   ├── scripts/                         # 추가 유틸리티
│   │   └── ingest_*.py                  # 데이터 인덱싱 스크립트
│   ├── config.py                        # 환경 변수 및 설정 로드
│   └── main.py                          # AI 서버 엔트리포인트
│
├── unigo/                               # Django 웹 애플리케이션
│   ├── unigo_app/                       # 메인 앱
│   │   ├── views.py                     # API 및 뷰 로직 (채팅, 인증)
│   │   ├── models.py                    # Django 모델 (Conversation, Message)
│   │   ├── urls.py                      # URL 라우팅
│   │   └── admin.py                     # 관리자 페이지 설정
│   ├── unigo/                           # 프로젝트 설정
│   │   ├── settings.py                  # Django 전역 설정
│   │   ├── urls.py                      # 루트 URL 설정
│   │   └── asgi.py/wsgi.py              # 서버 인터페이스
│   ├── templates/                       # HTML 템플릿 파일
│   │   └── unigo_app/
│   │       ├── base.html                # 기본 레이아웃 (헤더, 푸터 포함)
│   │       ├── auth.html                # 로그인/회원가입 페이지
│   │       ├── chat.html                # 메인 채팅 인터페이스
│   │       ├── character_select.html    # 캐릭터 선택 (온보딩)
│   │       └── setting.html             # 사용자 설정 페이지
│   ├── static/                          # 정적 자산
│   │   ├── css/                         # 스타일시트
│   │   │   ├── chat.css                 # 채팅 화면 스타일
│   │   │   ├── setting.css              # 설정 페이지 스타일
│   │   │   └── styles.css               # 공통 스타일
│   │   ├── js/                          # 클라이언트 스크립트
│   │   │   ├── chat.js                  # 채팅 로직 및 웹소켓 처리
│   │   │   ├── setting.js               # 설정 변경 핸들링
│   │   │   └── character_select.js      # 온보딩 인터랙션
│   │   └── images/                      # 이미지 자산 (캐릭터, 아이콘)
│   ├── media/                           # 사용자 업로드 파일
│   └── manage.py                        # Django 관리 명령
│
├── nginx/                               # Nginx 설정 파일
├── docs/                                # 개발 문서 및 회고록
├── docker-compose.yml                   # Docker 컨테이너 오케스트레이션
├── Dockerfile                           # Docker 이미지 빌드 설정
├── .env                                 # 환경 변수 (API Key, DB 접속 정보)
└── requirements.txt                     # Python 패키지 의존성 목록
```

---

## 5. 요구사항 명세서
<img width="1176" height="791" alt="Image" src="https://github.com/user-attachments/assets/f78a271f-b81e-422d-bdd2-706b0a70c1cb" />
https://www.notion.so/2c40413479c480458e42ebb6e116eef1

---

## 6. 화면 정의서
<img width="1171" height="697" alt="Image" src="https://github.com/user-attachments/assets/aa9b4107-e7db-4636-9e1d-0bf08622d1ee" />
https://www.figma.com/design/EQooVBPUshPncXDORTfJhB/%EC%9C%A0%EB%8B%88%EA%B3%A0?node-id=0-1&p=f&t=aAT9BriN4yCgShcK-0

---
## 7. WBS
<img width="1726" height="854" alt="image" src="https://github.com/user-attachments/assets/a2aa6bb0-6be0-43e4-9c00-4f7ee46d44e9" />
https://www.notion.so/1-Unigo-28b0413479c481999c87d8546598ca95

---


## 8. 주요 기능

### 1) 🤖 RAG 기반 AI 멘토

**ReAct(Reasoning + Acting) 패턴**을 적용한 AI 에이전트가 사용자의 질문을 분석하고 필요한 정보를 실시간으로 검색하여 답변합니다.

- **전공 탐색**: "인공지능 배우려면 무슨 과 가야 해?" -> 관련 학과 및 커리큘럼 소개
- **대학 검색**: "컴퓨터공학과 있는 서울 대학 어디야?" -> 개설 대학 목록 및 위치 정보 제공
- **진로 상담**: "기계공학과 나오면 취업 잘 돼?" -> 취업률, 평균 연봉, 주요 진출 분야(커리어넷 데이터 기준) 제공
- **입시 정보**: 각 대학 입학처의 수시/정시 모집요강 바로가기 링크 제공

### 2) 🎓 맞춤형 전공 추천 (온보딩)

사용자와의 초기 인터뷰(7가지 질문)를 통해 성향을 분석하고 최적의 전공을 추천합니다.

- **분석 요소**: 선호 과목, 관심사, 활동 유형, 선호 환경, 가치관, 관심 주제, 학습 스타일
- **알고리즘**: 사용자 프로필 벡터와 전공 특성 벡터 간의 다차원 유사도 분석 + 가중치 적용 점수 시스템

### 3) 🔑 사용자 경험 (UX)

- **회원가입/로그인**: 개인화된 대화 기록 및 추천 결과 저장
- **채팅 히스토리**: 이전 상담 내용을 언제든지 다시 확인 가능
- **마크다운 지원**: 가독성 높은 텍스트 및 클릭 가능한 링크 제공
- **페르소나 캐릭터**: 친근한 캐릭터(토끼 등) 기반 인터페이스

---

## 9. 기술 스택

| 분류          | 기술                     | 비고                                                |
| ------------- | ------------------------ | --------------------------------------------------- |
| **Backend**   | Python 3.11+, Django 5.x | 웹 프레임워크 및 API                                |
| **Data**      | MySQL                    | 관계형 데이터베이스 (전공/대학 정보, 사용자 데이터) |
| **AI / RAG**  | LangChain, LangGraph     | AI 에이전트 및 워크플로우 관리                      |
| **LLM**       | OpenAI GPT-4o-mini       | 추론 및 자연어 생성                                 |
| **Vector DB** | Pinecone                 | 고성능 벡터 검색                                    |
| **Frontend**  | HTML5, CSS3, Vanilla JS  | 반응형 웹 인터페이스                                |

---

## 10. 시스템 아키텍처 & 기술적 전략 (System Architecture & Technical Strategy)

### 1) 시스템 개요 (System Overview)

이 시스템은 Nginx 리버스 프록시 뒤에서 Django가 웹 애플리케이션과 AI 백엔드 로직을 모두 처리하는 **모듈러 모놀리스(Modular Monolith)** 아키텍처를 따릅니다.

```mermaid
flowchart TD
    %% 1. AWS 환경 (서버)
    subgraph AWS ["AWS EC2 Server"]
    %% 2. Docker 환경
    subgraph Docker ["Docker Environment"]
        direction TB

        subgraph Frontend ["Frontend"]
            Client["Client (Web)"]
        end

        Nginx["Nginx (Proxy)"]
        Gunicorn["Gunicorn (WSGI Server)"]

        subgraph Backend ["Django Backend"]
            Django["Django Application (Unigo)"]

            %% Django 내부 로직들
            UnigoApp["unigo_app (Chat/Auth)"]
            AIBackend["backend (LangGraph)"]
            MySQL[("MySQL Database")]
        end


    end
    end

    %% 3. 외부 클라우드/API 서비스
    subgraph CloudServices ["External Cloud Services"]
        Pinecone[("Pinecone Vector DB")]
        OpenAI["OpenAI API"]
    end


    %% 연결 관계 정의
    Client -->|HTTP| Nginx
    Nginx -->|Proxy Pass| Gunicorn
    Gunicorn --> Django

    %% Backend 내부 흐름
    Django -->|View Logic| UnigoApp
    Django -->|AI Logic call| AIBackend
    Django -->|ORM| MySQL

    %% AI 로직의 외부 통신
    AIBackend -->|Vector Search| Pinecone
    AIBackend -->|LLM API| OpenAI

    %% 스타일링
    classDef docker fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef backend fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;

    class Docker docker;
    class Backend backend;
```

### 2) 아키텍처 분석: Hybrid Approach (Django + SQLAlchemy)

이 프로젝트는 일반적인 웹 애플리케이션 프레임워크인 **Django**와 파이썬 데이터 생태계의 표준 ORM인 **SQLAlchemy**를 동시에 사용하는 하이브리드 구조를 채택하고 있습니다.

- **Django**: 웹 서비스의 '뼈대'를 담당
    - **역할**: 사용자 인증(Auth), 관리자 페이지(Admin), 정적 파일 관리, 엔드포인트 라우팅(Views).
    - **특징**: 생산성이 높고 보안 기능이 내장되어 있어 웹 서비스 구축에 효율적입니다.
- **SQLAlchemy**: AI/데이터 서비스의 '심장'을 담당
    - **역할**: RAG(검색 증강 생성)를 위한 벡터 메타데이터 관리, 대용량 데이터(전공, 대학 정보) 적재 및 조회, LangChain 등 AI 라이브러리와의 연동.
    - **위치**: `backend/db`, `backend/rag`, `backend/main.py` 등 AI 로직이 집중된 모듈에서 주로 사용됨.

### 3) SQLAlchemy를 사용이유

단순히 Django ORM만으로도 데이터베이스 조작이 가능함에도 불구하고, SQLAlchemy를 별도로 도입한 데에는 다음과 같은 강력한 기술적 이유가 존재합니다.

1.  **AI/Data 생태계와의 호환성 (Ecosystem Compatibility)**
    -   LangChain 및 대부분의 최신 AI 라이브러리(LlamaIndex 등)는 RAG 파이프라인 구축 시 **SQLAlchemy를 사실상의 표준(De-facto Standard)**으로 지원합니다.
    -   Django ORM은 프레임워크에 강하게 결합되어 있어 독립적인 AI 모듈에서 사용하기 무겁고 설정이 복잡한 반면, SQLAlchemy는 가볍고 독립적으로 동작하여 AI 모듈과의 결합이 자연스럽습니다.

2.  **성능 및 미세 제어 (Performance & Fine-grained Control)**
    -   **Bulk Operation**: `seed_all.py` 등 대용량 데이터 적재 시, SQLAlchemy Core를 사용하여 Raw SQL 수준의 성능을 내면서도 파이썬 객체로 관리할 수 있습니다.
    -   **Connection Pooling**: AI 모델 서빙과 같이 리소스 관리가 중요한 환경에서 `pool_pre_ping=True`, `pool_recycle=3600` 등 상세한 커넥션 풀 설정을 통해 DB 연결 안정성을 확보했습니다.

3.  **복잡한 데이터 타입 처리**: `Major` 모델의 `LONGTEXT` 컬럼에 JSON 데이터를 저장하는 등 비정규화된 패턴이나 커스텀 타입을 매핑할 때 훨씬 유연한 기능을 제공합니다.

### 4) 상세 분석: Django와 SQLAlchemy의 공존 (Co-existence Strategy)

시스템은 **"Django가 문지기(Gatekeeper) 역할을 하고, SQLAlchemy가 두뇌(Brain) 역할을 하는 구조"**입니다.

1.  **진입 (Entry)**: 사용자 프론트엔드가 Django 웹 서버(`unigo_app/views.py`)로 HTTP 요청을 보냅니다.
2.  **보안 및 인증 (Security)**: Django가 세션 인증, 권한 검사 등을 수행합니다. (Django ORM 사용)
3.  **위임 (Delegation)**: 유효한 요청이라면 Django View가 `backend.main.run_mentor()`를 호출하여 제어권을 AI 로직으로 넘깁니다.
4.  **AI 추론 (Inference)**: `run_mentor`는 LangGraph를 실행하며, 이 과정에서 필요한 데이터 조회는 SQLAlchemy를 통해 `Major`/`University` 테이블 및 Vector Store에 접근합니다.
5.  **응답 (Response)**: AI가 생성한 최종 답변 텍스트만 Django View로 반환되어 클라이언트에게 전달됩니다.

### 5) AI 도구 & 워크플로우 (AI Tools & Workflow)

AI 멘토는 **LangGraph**를 사용하여 상태 기반의 워크플로우를 관리하며, `backend/rag/tools.py`에 정의된 도구들을 사용하여 답변을 생성합니다.

```mermaid
flowchart TD
    Start(["Start"]) --> Agent["Agent Node<br/>(LLM Reasoning)"]
    Agent --> Check{"Tool Needed?"}
    Check -->|Yes| Tools["Tools Node<br/>(Execution)"]
    Check -->|No| Answer["Generate Answer"]
    Tools --> Agent
    Answer --> End(["End"])
    style Agent fill:#f9f,stroke:#333,stroke-width:2px
    style Tools fill:#bbf,stroke:#333,stroke-width:2px
```

### 6) 데이터베이스 클러스터 & 스키마 (Database Clusters & Schema)

데이터베이스는 크게 **세 가지 논리적 영역(Cluster)**으로 나뉘어 관리되고 있습니다.

1.  **User & Chat Cluster (Django)**: 사용자, 대화 기록, 프로필 관리 (웹 서비스 영역)
2.  **AI Data Cluster (SQLAlchemy)**: RAG/검색 엔진이 사용하는 전공 및 대학 원본 데이터 (AI 영역 - 핵심 데이터)
3.  **App Data Cluster (Django)**: Django Admin용으로 정의되었으나 AI 로직과는 분리된 영역

**주요 테이블 관계도**

| 모델명 (Model) | 관리 주체 | 설명 (Description) | 주요 필드 |
| :--- | :--- | :--- | :--- |
| **Major** | SQLAlchemy | 전공 상세 정보 (커리어넷) | `name`, `summary`, `salary`, `employment_rate` |
| **University** | SQLAlchemy | 대학 메타데이터 (대학어디가) | `name`, `campus_name`, `url`, `code` |
| **MajorUniversity** | SQLAlchemy | 전공-대학 매핑 (Mapping) | `major_id`, `university_id` |
| **Conversation** | Django | 채팅 세션 정보 | `session_id`, `user_id`, `created_at` |
| **Message** | Django | 채팅 메시지 내역 | `role`, `content`, `metadata` |
| **Suggestion** | Django | 온보딩 추천 결과 | `user_id`, `recommended_majors` (JSON) |

> **주의사항**: 두 개의 ORM이 하나의 DB를 공유하므로, 마이그레이션 시 주의가 필요합니다. `User/Chat` 영역은 Django `migrate`로, `AI Data` 영역은 `init_db.py` 등 별도 스크립트로 관리하여 두 영역의 충돌을 방지합니다.

#### 벡터 데이터베이스 (Pinecone)
- **`major_categories`**: 광범위한 매칭을 위한 표준 전공명 및 카테고리 임베딩.
- **`university_majors`**: 세밀한 의미 기반 검색을 위한 "대학명 + 학과명" 쌍의 임베딩.

#### ERD

```mermaid
erDiagram
    %% ==========================================
    %% 1. User & Chat Cluster (Django Native)
    %% ==========================================
    USER ||--|| USER_PROFILE : "has"
    USER ||--o{ CONVERSATION : "owns"
    USER ||--o{ MAJOR_RECOMMENDATION : "receives"
    CONVERSATION ||--o{ MESSAGE : "contains"

    USER {
        int id PK
        string username
        string email
        string password
    }

    USER_PROFILE {
        int id PK
        int user_id FK
        string character "페르소나 (rabbit 등)"
        string custom_image
    }

    CONVERSATION {
        int id PK
        int user_id FK "Nullable (비로그인 지원)"
        string session_id "Guest 식별용"
        string title
    }

    MESSAGE {
        int id PK
        int conversation_id FK
        string role "user/assistant"
        text content
        json metadata
    }

    MAJOR_RECOMMENDATION {
        int id PK
        int user_id FK
        json onboarding_answers
        json recommended_majors
    }

    %% ==========================================
    %% 2. AI Data Cluster (SQLAlchemy Managed)
    %% ** 실질적인 AI 데이터가 저장되는 곳 **
    %% ==========================================
    MAJOR_CATEGORY |{--|| MAJOR : "groups (JSON list)"

    MAJOR {
        int id PK
        string major_name "전공명"
        json relate_subject
        json university
        json chart_data
        float employment_rate
    }

    MAJOR_CATEGORY {
        int id PK
        string category_name
        json major_names
    }

    UNIVERSITY {
        int id PK
        string name
        string code
    }
```

---

## 11. 배포 과정 (Deployment)

### 배포 환경
- **Cloud Platform**: AWS EC2 / Azure VM
- **Web Server**: Nginx (Reverse Proxy)
- **WAS**: Gunicorn
- **Database**: MySQL, Pinecone (Serverless)

### 배포 파이프라인
1. **Source Control**: GitHub를 통한 코드 형상 관리
2. **Build**: `requirements.txt` 의존성 설치 및 정적 파일(`collectstatic`) 빌드
3. **Run**: Gunicorn을 사용하여 Django 애플리케이션 실행, Nginx가 80포트로 들어오는 요청을 Gunicorn 소켓으로 포워딩

---

## 12. 진행 과정 중 프로그램 개선 노력

### 1) AI 모델 최적화 (Hallucination Control)
- **Problem**: LLM이 없는 대학 정보(예: "한양대학교 천문학과")를 그럴듯하게 지어내는 환각 현상 발생.
- **Solution**: LangGraph의 System Prompt에 **"반드시 툴 검색 결과(Context)에 기반해서만 답변할 것"**이라는 강력한 제약 조건을 추가하고, 데이터 부재 시 솔직하게 "정보 없음"을 출력하도록 로직을 수정하여 신뢰성을 확보했습니다.

### 2) 데이터 검색 효율화 (Hybrid Search Strategy)
- **Problem**: 단순 벡터 검색으로는 "취업률 80% 이상" 같은 정확한 필터링 질의 처리가 어려움.
- **Solution**: **MySQL(정형 데이터 필터링)**과 **Pinecone(의미 기반 검색)**을 결합했습니다. 예를 들어, 사용자의 성향은 벡터로 검색하고, 구체적인 수치(연봉, 취업률)는 DB 값을 참조하도록 **이원화 전략**을 사용하여 검색 품질을 극대화했습니다.

### 3) 사용자 경험(UX) 개선 (Cold Start 해결)
- **Problem**: 사용자가 처음에 무엇을 물어봐야 할지 몰라 대화가 단절되는 '콜드 스타트' 현상 발생.
- **Solution**: **'온보딩 프로세스(성향 분석 7단계)'**를 도입하여, AI가 먼저 추천 전공을 제안하고 대화를 이끌어가는 **능동적 멘토링 UX**를 구현했습니다.

### 4) 시스템 성능 개선 (Graph Caching)
- **Problem**: 매 요청마다 그래프를 새로 빌드(Compile)하면서 응답 지연 발생.
- **Solution**: `get_graph()` 함수에 **싱글톤 패턴(Singleton Pattern)**을 적용하여, 한 번 빌드된 그래프 인스턴스를 메모리에 캐싱하고 재사용함으로써 응답 속도를 단축했습니다.

---

## 13. 트러블 슈팅 (Troubleshooting)

**Case 1: 이미지 업로드 갱신 불가 현상 (Image Overwrite)**
- **Problem**: Django의 기본 파일 저장 방식은 파일명 중복 시 자동으로 이름을 변경(`image_1.png`)하기 때문에, 사용자가 같은 파일명으로 이미지를 수정해도 반영되지 않는 문제가 있었습니다. 또한 브라우저의 강력한 캐싱으로 인해 변경 후에도 이전 이미지가 계속 표시되었습니다.
- **Solution**: 
  1. **물리적 삭제**: 파일 저장 직전 `delete(save=False)`를 호출하여 기존 파일을 삭제 후 저장하도록 `views.py` 로직을 수정했습니다.
  2. **Cache Busting**: 이미지 URL 호출 시 `?v={time.time()}`을 쿼리 스트링으로 붙여 브라우저가 매번 새로운 리소스로 인식하도록 강제했습니다.

**Case 2: 캐릭터 상태 비동기화 (State Sync)**
- **Problem**: 페이지 이동(새로고침) 시 로컬 스토리지와 서버 DB 간의 캐릭터 설정이 엇박자가 나면서 기본 캐릭터로 초기화되는 문제가 빈번했습니다.
- **Solution**: 
  1. 클라이언트의 `LocalStorage`를 UI의 기준으로 삼되,
  2. 앱 로드(`init`) 시점에 반드시 `/api/auth/me`를 호출하여 서버의 최신 데이터를 로컬 스토리지에 덮어씌우는 **"Server-First Synchronization"** 전략을 적용하여 일관성을 확보했습니다.

---

## 14. 테스트 계획 및 결과

### 테스트 계획
- **단위 테스트**: 각 LangChain Tool(검색, 조회)의 정상 동작 여부 검증
- **통합 테스트**: 사용자 질문 입력부터 최종 답변 생성까지의 전체 파이프라인 테스트
- **UI 테스트**: 반응형 레이아웃 및 크로스 브라우징 테스트 (Chrome, Edge)

### 테스트 결과
- **정확도**: 전공 추천 시나리오 50개 중 45개 이상 적절한 학과 추천 (정확도 90% 달성)
- **응답성**: 평균 응답 시간 2.5초 기록
- **안정성**: 예외 상황(데이터 없음 등)에 대한 Fallback 메시지 정상 출력 확인

---

## 15. 수행결과 (시연)

### 1) 로그인 및 회원가입
- 이메일/닉네임 중복 체크 및 보안 로그인

### 2) 온보딩 (성향 분석)
- **시나리오**: '추천 시작' 키워드로 시작 -> 7가지 성향 질문 응답 -> 가중치 기반 Top 5 학과 추천
- **결과**: 사용자의 관심사(예: "분석하는 일, 수학, 헬스")를 반영한 학과 추천 제공

### 3) 메인 채팅 & Tool Calling
- **시나리오 1 (학과 검색)**: "인공지능 관련된 학과들 다 알려줘" -> `list_departments` 호출
- **시나리오 2 (대학 검색)**: "연세대 컴퓨터 공학과 있어?" -> `get_universities_by_department` 호출
- **시나리오 3 (진로 정보)**: "컴퓨터공학과 졸업하면 연봉 어때?" -> `get_major_career_info` 호출
- **시나리오 4 (입시 정보)**: "서울대학교 입시 정보 알려줘." -> `get_university_admission_info` 호출
- **시나리오 5 (검색 도움)**: "사용법좀 알려줘." (잡담/검색 실패) -> `get_search_help` 호출

### 4) 설정 및 개인화
- 캐릭터 선택(토끼, 거북이 등) 및 커스텀 이미지 업로드
- "내 관심사 기억해?" -> 저장된 온보딩 정보 기반 답변 확인

---

## 16. 한 줄 회고

- **강지완**: "RAG 파이프라인을 구축하며 데이터 전처리의 중요성을 뼈저리게 느꼈습니다."
- **김진**: "LangGraph의 상태 관리를 통해 에이전트의 흐름을 제어하는 것이 흥미로웠습니다."
- **마한성**: "사용자 피드백을 반영하여 UI 디테일을 수정하는 과정에서 UX의 중요성을 배웠습니다."
- **오하원**: "팀원들과 함께 풀스택 개발 경험을 쌓을 수 있어 뜻깊은 시간이었습니다."
