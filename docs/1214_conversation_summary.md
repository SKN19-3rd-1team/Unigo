# 현재 Session에 대한 대화 요약 생성

**작성일**: 2025-12-13

## 설계 목표
사용자가 "지금까지 무슨 대화를 했는지" 빠르게 파악할 수 있도록 지원

## 개요:
- 사용자가 좌측 3번째 버튼을 클릭하면 
  현재까지의 대화 로그를 LLM에 전달하여 요약 생성
- 생성된 요약을 우측 패널에 표시
    - 로그인/비로그인 사용자 모두 이용 가능
    - 현재 활성 Session 기준 요약 (DB에 저장X → 일회성 UI 피드백 목적)  

## 방식 

### 1. 대화 요약 Tool 기반 방식
특정 시점에 대화 요약 tool을 LLM에게 호출
- 전체 대화 로그를 입력으로 사용하므로 토큰 비용 증가
- 장기 세션의 경우 성능 관리(구간 요약 등) 필요

```
Session 대화 로그
        ↓
summarize_conversation_history() tool
        ↓
요약 결과
        ↓
UI (우측 패널)
```

### 2. (langchain) ConversationSummaryMemory 기반 방식
LLM 모델이 잘 답하게 하기 위한 맥락 유지용 내부 메모리
- 모델 관점에서 중요하지 않다고 판단한 정보는 요약 과정에서 제거됨
- 사용자에게 보여주기에는 가독성이 부족 → 사용자 노출 목적에 용이하지 않음
- 요약 갱신 시점 제어 불가

활용 방안
- 내부 메모리를 한 번 더 LLM으로 재가공하여 UI용 포맷으로 변환
```
ConversationSummaryMemory
        ↓
재구조화 프롬프트
        ↓
요약 결과
        ↓
UI (우측 패널)
```

⚠️ 단, 이 과정 역시 내부 메모리를 다시 LLM에 입력해야 하므로 결과적으로 토큰 비용 절감 효과는 제한적


## 결론

대화 요약 Tool 기반 방식(1번)이 더 적합

### 백엔드
1. 대화 요약 로직
- `tools.py`: summarize_conversation_history() 함수 추가
    - 현재 Session의 대화 로그를 입력으로 받아 LLM을 통해 요약 생성
    - 요약 결과는 문자열로 반환하며 DB에는 저장하지 않음

2. 요약 API 엔드포인트
- `views.py`: summarize_conversation(request) API 엔드포인트 구현
    - 클라이언트로부터 전달받은 대화 로그를 summarize_conversation_history()에 전달
    - 생성된 요약 결과를 JSON 형태로 반환

### 프론트엔드
3. 요약 호출 및 UI 렌더링
- `chat.js`: summarizeConversation() 함수 추가
    - 좌측 세 번째 버튼 클릭 시 현재 Session의 대화 로그를 수집
    - 요약 API(/api/chat/summarize) 호출
    - 응답으로 받은 요약 결과를 우측 패널에 렌더링