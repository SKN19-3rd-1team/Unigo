# 2025-12-14 버그 수정 내역

## 수정 일시
2025년 12월 14일

## 발견된 문제

### 1. 캐릭터 선택 저장 실패 (403 Forbidden 에러)

**증상:**
- 캐릭터 선택 페이지(`/setting/character/`)에서 캐릭터를 선택하고 "선택 및 저장" 버튼 클릭 시 저장 실패
- 브라우저 콘솔에 403 Forbidden 에러 발생
- 에러 메시지: `Failed to load resource: the server responded with a status of 403 (Forbidden)`
- 영향을 받는 엔드포인트: `/api/setting/update-character`

**원인 분석:**
- `character_select.html` 파일의 JavaScript 코드에서 API 요청 시 CSRF 토큰이 누락됨
- Django는 POST 요청에 대해 CSRF 보호를 적용하므로, CSRF 토큰이 없으면 403 에러 반환
- 282-286번 라인의 `fetch` 요청 헤더에 `X-CSRFToken`이 포함되지 않음

**수정 내용:**

파일: `unigo/templates/unigo_app/character_select.html`

```diff
  const response = await fetch("/api/setting/update-character", {
    method: "POST",
-   headers: { "Content-Type": "application/json" },
+   headers: { 
+     "Content-Type": "application/json",
+     "X-CSRFToken": getCookie("csrftoken")
+   },
    body: JSON.stringify({ character: character.id }),
  });
```

**수정 위치:** 282-286번 라인

**참고:**
- `getCookie()` 함수는 `static/js/csrf.js`에 정의되어 있음
- `csrf.js`는 `base.html`에서 전역으로 로드되므로 모든 페이지에서 사용 가능

---

### 2. Pillow 의존성 누락

**증상:**
- Pillow 라이브러리가 설치되어 있지만 `requirements.txt`에 명시되지 않음
- 배포 시 의존성 설치 누락 가능성

**원인 분석:**
- Django의 `ImageField`는 Pillow 라이브러리를 필수로 요구함
- `UserProfile` 모델의 `custom_image` 필드가 `ImageField`를 사용
- 개발 환경에는 설치되어 있지만, 프로덕션 배포 시 누락될 수 있음

**수정 내용:**

파일: `requirements.txt`

```diff
  uvicorn==0.38.0
  zstandard==0.25.0
+ Pillow==10.0.0
```

**수정 위치:** 46번 라인 추가

---

## 코드 검토 결과

### 정상 작동하는 부분

1. **백엔드 API**
   - ✅ `upload_character_image` API (`views.py:441-470`)
   - ✅ `update_character` API (`views.py:414-438`)
   - ✅ `UserProfile` 모델 구조 (custom_image, use_custom_image 필드)
   - ✅ URL 라우팅 설정
   - ✅ 미디어 파일 서빙 설정 (MEDIA_URL, MEDIA_ROOT)

2. **프론트엔드**
   - ✅ `setting.js` - 이미지 업로드 로직
   - ✅ `csrf.js` - CSRF 토큰 헬퍼 함수
   - ✅ `setting.html` - 파일 업로드 UI
   - ✅ `base.html` - csrf.js 전역 로드

---

## 테스트 방법

### 캐릭터 선택 기능 테스트

1. 서버 실행: `python manage.py runserver`
2. 브라우저에서 `http://localhost:8000/setting/character/` 접속
3. 원하는 캐릭터 선택
4. "선택 및 저장" 버튼 클릭
5. 성공 메시지 확인: "{캐릭터명} 캐릭터가 선택되었습니다."
6. 설정 페이지로 리다이렉트되며 사이드바에 선택한 캐릭터 표시

### 이미지 업로드 기능 테스트

1. 설정 페이지 접속: `http://localhost:8000/setting/`
2. 사이드바의 "이미지 파일 업로드" 버튼 클릭
3. 이미지 파일 선택 (PNG, JPG 등)
4. 성공 메시지 확인: "이미지가 변경되었습니다."
5. 페이지 새로고침 후 사이드바에 업로드한 이미지 표시
6. 파일 저장 확인: `unigo/media/character_images/` 디렉토리

---

## 관련 파일

### 수정된 파일
- `unigo/templates/unigo_app/character_select.html` (CSRF 토큰 추가)
- `requirements.txt` (Pillow 의존성 추가)

### 검토한 파일
- `unigo/unigo_app/views.py` (upload_character_image, update_character)
- `unigo/unigo_app/models.py` (UserProfile)
- `unigo/unigo_app/urls.py`
- `unigo/static/js/setting.js`
- `unigo/static/js/csrf.js`
- `unigo/templates/unigo_app/setting.html`
- `unigo/templates/unigo_app/base.html`
- `unigo/unigo/settings.py` (MEDIA 설정)
- `unigo/unigo/urls.py` (미디어 파일 서빙)

---

## 추가 참고사항

### CSRF 토큰 사용 패턴

Django에서 POST 요청 시 CSRF 토큰을 포함하는 방법:

```javascript
// 방법 1: getCookie 함수 사용
headers: {
  'Content-Type': 'application/json',
  'X-CSRFToken': getCookie('csrftoken')
}

// 방법 2: getPostHeaders 함수 사용 (JSON 요청)
headers: getPostHeaders()

// 방법 3: FormData 사용 시 (파일 업로드)
headers: {
  'X-CSRFToken': getCookie('csrftoken')
  // Content-Type은 브라우저가 자동 설정
}
```

### ImageField 사용 시 필수 설정

1. Pillow 설치: `pip install Pillow`
2. `settings.py`에 MEDIA 설정:
   ```python
   MEDIA_URL = '/media/'
   MEDIA_ROOT = BASE_DIR / 'media'
   ```
3. `urls.py`에 미디어 파일 서빙 설정 (개발 환경):
   ```python
   if settings.DEBUG:
       urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
   ```
