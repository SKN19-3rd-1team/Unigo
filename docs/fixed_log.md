# 수정 로그 - page4 기능 개선

1. **네비게이션 동작**
   - `page1/index.html`, `page2/index.html`, `page4/index.html`에서 `Chat` 메뉴가 page4로 이동(또는 해당 페이지에 머무르도록)하도록 수정했습니다.

2. **page4 레이아웃 및 스타일**
   - `page4/index.html`을 공통 레이아웃 구조에 맞게 재구성하고, 대화 말풍선과 우측 추천 패널, `assets/rabbit.png` 이미지를 추가했습니다. 향후 챗봇 결과 데이터를 표시할 수 있도록 TODO 주석을 남겼습니다.
   - `page4/styles.css`에 말풍선 스타일(사용자 질문은 흰색, 응답은 분홍색), 패널 높이 고정, 좌측 패널만 스크롤 처리 등 화면을 묘사한 스타일을 적용했습니다.

3. **상호작용 및 상태 유지**
   - `page4/script.js`에서 입력창 전송(버튼/Enter) 시 분홍색 말풍선이 추가되도록 기능을 구현했습니다.
   - 세션 기반 저장을 추가하여 다른 화면으로 이동했다가 돌아와도 대화 내역이 유지되며, 새로고침 시에는 기록이 초기화되도록 했습니다.

4. **전공 추천 누락 오류 수정** (2025-12-07 20:24)
   - **문제 상황**: 사용자가 온보딩 과정에서 직접 입력한 '희망 전공'(예: 컴퓨터공학과)이 로그상으로는 점수가 5.0 등으로 높게 책정되었음에도, 최종 추천 리스트(Top 5)에는 포함되지 않는 현상이 발생했습니다.
   - **원인 분석**:
     - `recommend_majors_node` 함수에서 선호 전공에 대해 `aggregated_scores` 점수는 올바르게 업데이트(Boosting)하고 있었습니다.
     - 그러나 최종 순위를 매기는 `_summarize_major_hits` 함수는 벡터 검색 결과인 `hits` 리스트만을 순회하며 요약 정보를 생성합니다.
     - 선호 전공이 초기 벡터 검색 결과(Top 50)에 포함되지 않은 경우, 점수는 높지만 `hits` 목록에 해당 전공의 정보 객체(SearchHit)가 없어 최종 결과 집계에서 제외되었습니다.
   - **조치 내용**: `backend/graph/nodes.py` 수정
     - 선호 전공이 기존 검색 결과(`hits`)에 없는 경우, 해당 전공 정보를 담은 **Synthetic SearchHit(합성 검색 결과 객체)**를 강제로 생성하여 `hits` 리스트에 추가하도록 로직을 보완했습니다.
     - 이를 통해 벡터 유사도가 낮더라도 사용자가 명시적으로 언급한 전공이 최종 추천 목록에 정상적으로 노출되도록 수정했습니다.

5. **사용자 인증 및 DB/대화 기록 시스템 구축** (2025-12-08)
   
   **Frontend (Template & JS)**
   - `templates/unigo_app/base.html`: 로그인/회원가입 모달 구조 복구 및 입력 필드에 `id` 속성(`login-email` 등) 추가, 라벨 개선("이메일 또는 아이디").
   - `static/js/script.js`: 로그인(`/api/auth/login`) 및 회원가입(`/api/auth/signup`) API 호출 로직 구현. 성공 시 자동 리다이렉트 처리.
   - `templates/unigo_app/header.html`: 로그인 상태에 따라 Login/Logout 버튼 조건부 렌더링 적용 (Django Template Tag 사용).
   - `views.py/home`: 루트 경로 접속 시 로그인 상태에 따라 `/chat` 또는 `/auth`로 자동 리다이렉트(Redirect) 로직 추가.

   **Backend (Django Auth & Models)**
   - **모델 구현 (`models.py`)**:
     - `Conversation`: 사용자별/세션별 대화 기록 저장 (로그인/비로그인 모두 지원).
     - `Message`: 대화 메시지 저장 (`role`, `content` 포함).
     - `MajorRecommendation`: 온보딩 결과 저장.
     - `Major`, `University`: 전공 및 대학 데이터 적재용 모델.
   - **인증 API (`views.py`)**:
     - `auth_login`: **이메일 또는 Username** 중 하나로 로그인 가능하도록 유연한 인증 로직 구현.
     - `auth_signup`: 회원가입 시 자동 로그인 처리.
   - **기능 API 업데이트**:
     - `chat_api`, `onboarding_api`: DB에 대화 및 추천 결과를 실시간으로 저장하도록 수정.

   **Data Management**
   - **마이그레이션 도구 (`management/commands/load_major_data.py`)**:
     - `backend/data/major_detail.json`의 대용량 전공 데이터를 Django DB 모델로 적재하는 커맨드 개발.
     - 실행: `python manage.py load_major_data`
