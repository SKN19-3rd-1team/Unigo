# 로컬 Docker 테스트 가이드

이 문서는 AWS EC2에 배포하기 전, 로컬 환경(Windows/WSL 등)에서 Docker를 활용해 프로젝트가 정상 작동하는지 확인하는 방법을 설명합니다.

## 1. 사전 준비 (Prerequisites)

1. **Docker Desktop 설치**: Windows 환경이라면 Docker Desktop이 설치되어 있고 실행 중이어야 합니다.
2. **프로젝트 경로 이동**: 터미널(WSL, Git Bash 등)에서 프로젝트 루트 디렉토리(`Unigo/`)로 이동합니다.

## 2. 환경 설정

로컬 테스트를 위해서도 `.env` 파일이 필요합니다.

1. `.env` 파일이 없다면 생성합니다.

    ```bash
    cp .env.example .env
    ```

2. (선택 사항) 로컬 테스트이므로 `DEBUG=True`로 두셔도 됩니다. DB 설정 등은 `docker-compose.yml`이 자동으로 처리해주므로 `.env`에 특별한 DB 설정이 없어도 기본값으로 동작하게 구성되어 있습니다(단, `MYSQL_PASSWORD` 등은 일치해야 함).

## 3. Docker 실행

터미널에서 다음 명령어를 입력합니다.

```bash
# 이미지를 빌드하고 백그라운드에서 실행
docker compose up -d --build
```

- `-d`: 백그라운드 모드 (터미널을 계속 쓸 수 있음)
- `--build`: 코드가 변경되었다면 이미지를 새로 만듦

## 4. 접속 및 확인

1. **웹 브라우저 접속**:
    - 주소창에 `http://localhost` 입력을 시도합니다.
    - Nginx가 80번 포트에서 대기하고 있다가 Django(8000번)로 연결해줍니다.

2. **로그 확인**:
    - 실행 중에 에러가 없는지 실시간 확인:

    ```bash
    docker compose logs -f
    ```

    - `ctrl + c`를 누르면 로그 확인을 종료합니다(서버는 안 꺼짐).

3. **초기 세팅 (최초 1회)**:
    - DB 테이블 생성 및 관리자 계정 생성이 필요할 수 있습니다.

    ```bash
    # DB 마이그레이션
    docker compose exec web python manage.py migrate
    
    # 관리자 계정 생성
    docker compose exec web python manage.py createsuperuser
    ```

## 5. 테스트 종료

테스트가 끝났다면 다음 명령어로 컨테이너를 정리합니다.

```bash
# 컨테이너 중지 및 삭제
docker compose down
```

- 데이터(`mysql_data` 볼륨)는 `down`을 해도 지워지지 않고 남아있습니다.
- 데이터를 완전히 초기화하고 싶다면: `docker compose down -v`
