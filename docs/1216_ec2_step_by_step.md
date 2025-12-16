# AWS EC2 배포 가이드 (Step-by-Step)

로컬에서 테스트를 마쳤으므로, AWS EC2(Ubuntu) 서버에 실배포하는 과정을 상세히 안내합니다.

## 1. 전제 조건 (Prerequisites)

- AWS EC2 인스턴스가 생성되어 있어야 합니다 (OS: Ubuntu 22.04 LTS 권장).
- 보안 그룹(Security Group)에서 다음 포트가 열려 있어야 합니다.
  - **SSH (22)**: 관리자 접속용
  - **HTTP (80)**: 웹 서비스용

## 2. 서버 접속 및 기본 세팅

터미널(또는 PuTTY)을 열고 EC2에 SSH로 접속합니다.

```bash
# 예시
ssh -i "key.pem" ubuntu@<EC2_PUBLIC_IP>
```

접속 후, 패키지들을 최신화하고 Docker를 설치합니다.

```bash
# 1. 패키지 업데이트
sudo apt update && sudo apt upgrade -y

# 2. Docker 자동 설치 스크립트 실행
curl -fsSL https://get.docker.com | sudo sh

# 3. sudo 없이 docker 명령어 쓰도록 권한 부여 (중요)
sudo usermod -aG docker $USER

# 4. 그룹 변경 사항 적용 (로그아웃 없이 적용)
newgrp docker
```

## 3. 프로젝트 코드 가져오기

GitHub 등에서 코드를 클론합니다.

```bash
# 예시: git clone
git clone <YOUR_REPOSITORY_URL>
cd Unigo
```

## 4. 배포용 설정 (`.env`, `docker-compose.prod.yml`)

### 4.1. `.env` 파일 생성

서버에는 `.env` 파일이 없으므로 새로 만들어야 합니다.

```bash
cp .env.example .env
nano .env
```

**[서버용 .env 주의사항]**

- `DEBUG=False` 로 변경 (보안 필수)
- `MYSQL_HOST` 값은 `docker-compose.prod.yml`이 알아서 덮어쓰므로 상관없지만, 헷갈리지 않게 그냥 두거나 `db`로 적으셔도 됩니다.
- **`SECRET_KEY`**: 배포용 복잡한 키로 변경 추천.

### 4.2. 실행 (Production 모드)

우리는 로컬과 달리 **서버에서는 DB 컨테이너가 필요**하므로, 제가 만들어드린 `docker-compose.prod.yml`을 사용해야 합니다.

```bash
# -f 옵션으로 prod 파일 지정하여 실행
docker compose -f docker-compose.prod.yml up -d --build
```

## 5. 초기 데이터 및 설정

컨테이너가 실행되었다면, 데이터베이스 초기화가 필요합니다.

```bash
# 1. DB 마이그레이션 (테이블 생성)
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# 2. 정적 파일 모으기 (CSS/JS 등)
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# 3. 관리자 계정 생성 (Admin 페이지 접속용)
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

## 6. 접속 확인

브라우저 주소창에 `http://<EC2_PUBLIC_IP>` 를 입력하여 접속되는지 확인합니다.

---

## 💡 로컬 vs 서버 차이점 요약 (중요)

| 구분          | 로컬 (Local/Laptop)                               | 서버 (EC2 Production)                              |
| :------------ | :------------------------------------------------ | :------------------------------------------------- |
| **설정 파일** | `docker-compose.yml`                              | `docker-compose.prod.yml`                          |
| **DB 위치**   | **Windows Host** (172... or host.docker.internal) | **Docker 내부 컨테이너** (`db` 서비스)             |
| **명령어**    | `docker compose up ...`                           | `docker compose -f docker-compose.prod.yml up ...` |

## 7. 서버 중지 및 초기화

서버를 종료하거나 완전히 초기화해야 할 때는 다음 명령어를 사용합니다.

```bash
# 단순 중지 및 컨테이너 삭제
docker compose -f docker-compose.prod.yml down

# 완전 초기화 (이미지, 볼륨, 컨테이너 모두 삭제)
docker compose -f docker-compose.prod.yml down --rmi all -v --remove-orphans
```

- `-v` 옵션은 데이터베이스 볼륨까지 삭제하므로 **실서버 데이터가 날아갑니다. 주의하세요!**
