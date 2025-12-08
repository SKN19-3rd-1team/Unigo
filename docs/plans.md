# Unigo 프로젝트 개발 계획 및 아키텍처

**최종 업데이트**: 2025-12-08

## 📋 프로젝트 개요

Unigo는 LangGraph와 RAG(Retrieval Augmented Generation)를 활용한 AI 기반 대학 전공 추천 및 입시 정보 제공 챗봇 시스템입니다.

### 핵심 목표
1. 학생들의 관심사와 적성에 맞는 전공 추천
2. 전공별 상세 정보 제공 (과목, 진로, 연봉 등)
3. 대학별 입시 정보 제공
4. 자연스러운 대화형 인터페이스

## 🏗️ 시스템 아키텍처

### 전체 구조

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Django)                     │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Templates  │  │  Static JS   │  │  Static CSS  │       │
│  │  (HTML)     │  │  (chat.js)   │  │  (chat.css)  │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                    ┌───────▼────────┐                        │
│                    │  Django Views  │                        │
│                    │  (API Layer)   │                        │
│                    └───────┬────────┘                        │
└────────────────────────────┼──────────────────────────────────┘
                             │
                    ┌────────▼─────────┐
                    │  Backend (RAG)   │
                    │  ┌────────────┐  │
                    │  │ LangGraph  │  │
                    │  │  (ReAct)   │  │
                    │  └─────┬──────┘  │
                    │        │         │
                    │  ┌─────▼──────┐  │
                    │  │   Tools    │  │
                    │  │ (검색/추천) │  │
                    │  └─────┬──────┘  │
                    │        │         │
                    │  ┌─────▼──────┐  │
                    │  │  Pinecone  │  │
                    │  │ Vector DB  │  │
                    │  └────────────┘  │
                    └──────────────────┘
                             │
                    ┌────────▼─────────┐
                    │   OpenAI API     │
                    │  (GPT + Embed)   │
                    └──────────────────┘
```

## 🔄 데이터 플로우

### 1. 온보딩 플로우

```
사용자 접속
    │
    ▼
온보딩 질문 1: 선호 과목
    │
    ▼
온보딩 질문 2: 흥미/취미
    │
    ▼
온보딩 질문 3: 희망 연봉
    │
    ▼
온보딩 질문 4: 희망 학과
    │
    ▼
답변 수집 완료
    │
    ▼
POST /api/onboarding
    │
    ▼
Backend: run_major_recommendation()
    │
    ├─► LLM으로 전공명 정규화
    │
    ├─► Pinecone 벡터 검색 (Top 50)
    │
    ├─► 선호 전공 별도 검색
    │
    ├─► 차등 점수 부여 (Tier 1-4)
    │
    └─► 최종 추천 목록 생성
    │
    ▼
Frontend: 추천 결과 표시
    │
    ├─► 채팅창에 TOP 5 요약
    │
    └─► 우측 패널에 상세 정보
```

### 2. 대화 플로우 (ReAct 패턴)

```
사용자 질문 입력
    │
    ▼
POST /api/chat
    │
    ▼
Backend: run_mentor()
    │
    ▼
LangGraph Agent (ReAct)
    │
    ├─► LLM이 질문 분석
    │
    ├─► 필요한 Tool 선택
    │   │
    │   ├─► list_departments
    │   ├─► get_universities_by_department
    │   ├─► get_major_career_info
    │   ├─► get_university_admission_info
    │   └─► get_search_help
    │
    ├─► Tool 실행 및 결과 수집
    │
    ├─► LLM이 결과 종합
    │
    └─► 최종 답변 생성
    │
    ▼
Frontend: 답변 표시
    │
    └─► Markdown 링크 파싱
```

## 🎯 핵심 기능 구현

### 1. 차등 점수 시스템 (Tiered Scoring)

**위치**: `backend/graph/nodes.py`

**목적**: 사용자가 명시한 희망 전공을 정확도에 따라 우선순위 부여

**구현**:
```python
# 점수 상수 정의
SCORE_TIER_1_EXACT_MATCH = 20.0      # 정확 일치
SCORE_TIER_2_STARTS_WITH = 15.0      # 접두어 일치
SCORE_TIER_3_CONTAINS = 10.0         # 포함
SCORE_TIER_4_VECTOR_MATCH = 5.0      # 벡터 검색

# 점수 부여 로직
if rec_name == pref_key:
    boost_score = SCORE_TIER_1_EXACT_MATCH
elif rec_name.startswith(pref_key):
    boost_score = SCORE_TIER_2_STARTS_WITH
elif pref_key in rec_name:
    boost_score = SCORE_TIER_3_CONTAINS
else:
    boost_score = SCORE_TIER_4_VECTOR_MATCH
```

**효과**:
- 사용자가 "컴퓨터공학과"를 입력하면 정확히 일치하는 전공이 1위
- 유사 전공("컴퓨터교육과" 등)은 낮은 점수로 하위 순위

### 2. LLM 기반 전공명 정규화

**위치**: `backend/graph/nodes.py` - `_normalize_majors_with_llm()`

**목적**: 사용자 입력의 줄임말/오타를 표준 전공명으로 변환

**예시**:
- "컴공" → "컴퓨터공학과"
- "화공" → "화학공학과"
- "경영" → "경영학과"

**구현**:
```python
def _normalize_majors_with_llm(raw_majors: list[str]) -> list[str]:
    prompt = (
        "사용자가 입력한 대학 전공명(줄임말, 오타 포함)을 "
        "가장 적절한 '표준 학과명'으로 변환해주세요."
    )
    response = llm.invoke(prompt)
    return normalized_list
```

### 3. ReAct 패턴 에이전트

**위치**: `backend/graph/nodes.py` - `agent_node()`

**목적**: LLM이 자율적으로 필요한 정보를 검색하도록 함

**특징**:
- LLM이 사용자 질문을 분석하여 적절한 Tool 선택
- Tool 실행 결과를 바탕으로 답변 생성
- 필요시 여러 Tool을 순차적으로 호출

**강제 Tool 사용 메커니즘**:
```python
# LLM이 Tool 없이 답변하려 하면 차단
if not has_tool_results and not response.tool_calls:
    error_message = HumanMessage(content="반드시 툴을 호출해야 합니다.")
    messages.append(error_message)
    response = llm_with_tools.invoke(messages)
```

### 4. Markdown 링크 파싱

**위치**: `unigo/static/js/chat.js` - `createBubble()`

**목적**: 챗봇 응답의 Markdown 링크를 클릭 가능한 HTML로 변환

**구현**:
```javascript
formattedText = formattedText.replace(
    /\[([^\]]+)\]\(([^)]+)\)/g,
    '<a href="$2" target="_blank" style="color:#0066cc;">$1</a>'
);
```

**효과**:
- `[한양대 입시정보](URL)` → 클릭 가능한 링크
- 새 탭에서 열림 (`target="_blank"`)

## 📊 데이터 구조

### 전공 데이터 (major_detail.json)

```json
{
  "dataSearch": {
    "content": [
      {
        "major": "컴퓨터공학과",
        "cluster": "공학계열",
        "summary": "컴퓨터 하드웨어와 소프트웨어...",
        "interest": "컴퓨터, 프로그래밍에 관심이 있는 학생...",
        "property": "논리적 사고력, 문제 해결 능력...",
        "relate_subject": [...],
        "job": "소프트웨어 개발자, 데이터 과학자...",
        "salary": 4500,
        "university": [...]
      }
    ]
  }
}
```

### Pinecone 벡터 인덱스

**문서 타입**:
- `summary`: 전공 요약
- `interest`: 관심사/적성
- `property`: 특성/역량
- `subjects`: 관련 과목
- `jobs`: 진출 직업

**메타데이터**:
```python
{
    "major_id": "computer-science",
    "major_name": "컴퓨터공학과",
    "doc_type": "summary",
    "cluster": "공학계열",
    "salary": 4500,
    "relate_subject_tags": ["수학", "물리"],
    "job_tags": ["개발자", "엔지니어"]
}
```

## 🔧 개발 단계

### Phase 1: 기본 구조 (완료 ✅)
- Django 프로젝트 설정
- Backend 통합
- 기본 채팅 UI

### Phase 2: 온보딩 시스템 (완료 ✅)
- 4가지 질문 구현
- 전공 추천 API
- 결과 표시 UI

### Phase 3: 차등 점수 시스템 (완료 ✅)
- Tier 기반 점수 부여
- LLM 정규화
- 중복 부스팅 방지

### Phase 4: 코드 리팩토링 (완료 ✅)
- 매직 넘버 → 상수
- Docstring 추가
- 디렉토리 구조 정리

### Phase 5: 향후 계획 (예정 🔄)
- [ ] 사용자 인증 시스템
- [ ] 대화 기록 저장 (DB)
- [ ] 추천 결과 북마크
- [ ] 전공 비교 기능
- [ ] 모바일 최적화

## 🎨 UI/UX 설계 원칙

### 1. 대화형 인터페이스
- 자연스러운 대화 흐름
- 즉각적인 피드백 (로딩 인디케이터)
- 명확한 사용자/AI 구분

### 2. 정보 계층화
- 채팅창: 요약 정보
- 우측 패널: 상세 정보
- 클릭 가능한 링크: 외부 자료

### 3. 접근성
- 키보드 네비게이션 지원
- 명확한 색상 대비
- 스크린 리더 호환

## 📈 성능 최적화

### 1. 벡터 검색 최적화
- Top-K 제한 (기본 50개)
- 문서 타입별 가중치 적용
- 중복 제거

### 2. LLM 호출 최적화
- 프롬프트 최소화
- 스트리밍 응답 (향후)
- 캐싱 (향후)

### 3. 프론트엔드 최적화
- 세션 스토리지 활용
- 불필요한 재렌더링 방지
- 이미지 최적화

## 🔐 보안 고려사항

### 현재 구현
- CSRF 면제 (`@csrf_exempt`) - API 엔드포인트만
- 환경 변수로 API 키 관리
- `.gitignore`로 민감 정보 제외

### 향후 개선
- [ ] CSRF 토큰 적용
- [ ] Rate limiting
- [ ] 입력 검증 강화
- [ ] SQL Injection 방지 (DB 사용 시)

---

**참고 문서**:
- [실행 가이드](guide.md)
- [수정 로그](fixed_log.md)
- [README](../README.md)
