import json
import os
from django.core.management.base import BaseCommand
from unigo_app.models import Major, University, MajorUniversity
from django.db import transaction

class Command(BaseCommand):
    help = 'Load major data from backend/data/major_detail.json to database'

    def handle(self, *args, **options):
        # 1. 파일 경로 찾기
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        # unigo/unigo_app/management/commands -> unigo/unigo_app/management -> unigo/unigo_app -> unigo -> frontend
        # But actually BASE_DIR in settings is usually unigo (project root) or frontend.
        # Let's try relative path from current file to backend
        
        # frontend/unigo/unigo_app/management/commands/load_major_data.py
        # frontend/backend/data/major_detail.json
        # Go up 4 levels to frontend
        frontend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
        json_path = os.path.join(frontend_dir, 'backend', 'data', 'major_detail.json')

        if not os.path.exists(json_path):
            self.stdout.write(self.style.ERROR(f'File not found: {json_path}'))
            return

        self.stdout.write(f'Loading data from {json_path}...')

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading JSON: {e}'))
            return

        # 2. 데이터 파싱 및 저장
        # JSON 구조: [{"dataSearch": {"content": [{...}, {...}]}}] (예상)
        # 하지만 실제 파일 내용을 보니 array of objects, each has dataSearch -> content list
        
        self.stdout.write('Parsing data...')
        
        success_count = 0
        error_count = 0

        with transaction.atomic():
            # 기존 데이터 정리 (선택사항, 중복 방지를 위해 삭제 후 재생성하거나 get_or_create 사용)
            # 여기서는 안전하게 get_or_create로 처리
            pass

            for item in data:
                content_list = item.get('dataSearch', {}).get('content', [])
                for major_data in content_list:
                    try:
                        name = major_data.get('major')
                        if not name:
                            continue
                            
                        # Major 저장
                        major, created = Major.objects.update_or_create(
                            name=name,
                            defaults={
                                'cluster': _get_cluster(name), # 계열 정보가 JSON에 없으면 추론하거나 빈값
                                'summary': major_data.get('summary', ''),
                                'interest': major_data.get('interest', ''),
                                'property': major_data.get('property', ''),
                                'salary': _parse_salary(major_data.get('salary')),
                                'employment_rate': major_data.get('employment', ''),
                                'department': major_data.get('department', ''),
                                'relate_subjects': major_data.get('relate_subject', []),
                                'career_activities': major_data.get('career_act', []),
                                'jobs': major_data.get('job', ''),
                                'qualifications': major_data.get('qualifications', ''),
                                'enter_fields': major_data.get('enter_field', []),
                                'main_subjects': major_data.get('main_subject', []),
                                'chart_data': major_data.get('chartData', []),
                            }
                        )
                        
                        # University 저장 및 연결
                        uni_list = major_data.get('university', [])
                        for uni_data in uni_list:
                            uni_name = uni_data.get('schoolName')
                            if not uni_name:
                                continue
                                
                            uni, _ = University.objects.get_or_create(
                                name=uni_name,
                                campus_name=uni_data.get('campus_nm', '제1캠퍼스'),
                                defaults={
                                    'area': uni_data.get('area', ''),
                                    'school_url': uni_data.get('schoolURL', ''),
                                }
                            )
                            
                            MajorUniversity.objects.get_or_create(
                                major=major,
                                university=uni,
                                defaults={
                                    'major_name_at_university': uni_data.get('majorName', name)
                                }
                            )
                        
                        success_count += 1
                        if success_count % 100 == 0:
                            self.stdout.write(f'Processed {success_count} majors...')
                            
                    except Exception as e:
                        error_count += 1
                        self.stdout.write(self.style.WARNING(f'Error processing {name}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully loaded {success_count} majors. Errors: {error_count}'))

def _parse_salary(salary_str):
    if not salary_str:
        return 0
    try:
        return float(salary_str)
    except ValueError:
        return 0

def _get_cluster(major_name):
    # JSON에 cluster 필드가 없어서 임시로 처리
    # 추후 major_categories.json을 활용하거나 별도 로직 필요
    if "공학" in major_name: return "공학계열"
    if "경영" in major_name or "경제" in major_name: return "사회계열"
    if "어문" in major_name or "국어" in major_name: return "인문계열"
    if "예술" in major_name or "디자인" in major_name: return "예체능계열"
    if "의학" in major_name or "간호" in major_name: return "의약계열"
    return "기타"
