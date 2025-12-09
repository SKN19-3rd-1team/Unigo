import sys
from pathlib import Path

# sys.path에 프로젝트 루트 추가
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.append(str(project_root))

import json  # noqa: E402
from backend.db.connection import engine, SessionLocal, Base  # noqa: E402
from backend.db.models import Major  # noqa: E402
from backend.rag.loader import load_major_detail  # noqa: E402
from sqlalchemy import text  # noqa: E402


def extract_stat_value(value):
    if isinstance(value, str):
        value = value.strip()
        if value.startswith("[") or value.startswith("{"):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass

    if isinstance(value, list):
        for item in value:
            # item은 보통 {'item': '전체', 'data': '56.3'} 같은 dict 형태임
            if isinstance(item, dict) and item.get("item") == "전체":
                try:
                    return float(item.get("data", 0))
                except (ValueError, TypeError):
                    return None
        # '전체' 항목이 없을 경우 대체 처리 (첫 번째 항목 사용)
        if value and isinstance(value[0], dict):
            try:
                return float(value[0].get("data", 0))
            except (ValueError, TypeError):
                return None

    try:
        if value:
            return float(value)
    except (ValueError, TypeError):
        pass
    return None


def migrate():
    print("🚀 MySQL로 마이그레이션 시작...")

    # 연결 확인
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ 데이터베이스 연결 성공.")
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        print(".env 파일과 MySQL 서버 상태를 확인해주세요.")
        return

    # 테이블 생성
    print("🛠️ 테이블 생성 중...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ 테이블 생성 완료.")

    # JSON에서 데이터 로드
    print("📂 major_detail.json에서 데이터 로드 중...")
    records = load_major_detail()
    print(f"✅ JSON에서 {len(records)}개의 레코드 로드됨.")

    # DB에 삽입
    db = SessionLocal()
    try:
        # 기존 데이터 삭제? (필요시 주석 해제)
        # db.query(Major).delete()

        count = 0
        for record in records:
            # 존재 여부 확인
            try:
                exists = (
                    db.query(Major).filter(Major.major_id == record.major_id).first()
                )
                if exists:
                    print(f"⚠️ 중복 건너뜀: {record.major_name} ({record.major_id})")
                    continue

                major_entry = Major(
                    major_id=record.major_id,
                    major_name=record.major_name,
                    cluster=json.dumps(record.cluster, ensure_ascii=False)
                    if isinstance(record.cluster, (dict, list))
                    else record.cluster,
                    summary=record.summary,
                    interest=record.interest,
                    property=record.property,
                    job=record.job,
                    relate_subject=json.dumps(record.relate_subject, ensure_ascii=False)
                    if record.relate_subject
                    else None,
                    enter_field=json.dumps(record.enter_field, ensure_ascii=False)
                    if record.enter_field
                    else None,
                    department_aliases=json.dumps(
                        record.department_aliases, ensure_ascii=False
                    )
                    if record.department_aliases
                    else None,
                    career_act=json.dumps(record.career_act, ensure_ascii=False)
                    if record.career_act
                    else None,
                    qualifications=json.dumps(record.qualifications, ensure_ascii=False)
                    if record.qualifications
                    else None,
                    main_subject=json.dumps(record.main_subject, ensure_ascii=False)
                    if record.main_subject
                    else None,
                    university=json.dumps(record.university, ensure_ascii=False)
                    if record.university
                    else None,
                    chart_data=json.dumps(record.chart_data, ensure_ascii=False)
                    if record.chart_data
                    else None,
                    raw_data=json.dumps(record.raw, ensure_ascii=False)
                    if record.raw
                    else None,
                    salary=extract_stat_value(record.salary),
                    employment=json.dumps(record.employment, ensure_ascii=False)
                    if isinstance(record.employment, (dict, list))
                    else record.employment,
                    employment_rate=extract_stat_value(record.employment_rate),
                    acceptance_rate=extract_stat_value(record.acceptance_rate),
                )

                db.add(major_entry)
                # db.flush()  # 최적화: 디버깅 아니면 매번 flush 하지 않음
                count += 1
            except Exception as e:
                print(f"❌ 삽입 오류 {record.major_name}: {e}")
                for k, v in record.__dict__.items():
                    if isinstance(v, dict):
                        print(f"   필드 '{k}'는 DICT입니다! 값: {str(v)[:100]}")
                    if isinstance(v, list):
                        print(f"   필드 '{k}'는 LIST입니다! 값: {str(v)[:100]}")
                # 파일에도 로그 기록
                with open("migration_error.log", "w", encoding="utf-8") as f:
                    f.write(f"Error inserting: {record.major_name}\n")
                    f.write(str(e) + "\n")
                    import traceback

                    f.write(traceback.format_exc())
                db.rollback()
                break

        db.commit()
        print(f"✅ {count}개의 새 레코드가 성공적으로 삽입되었습니다.")

    except Exception as e:
        print(f"❌ 전역 오류: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
