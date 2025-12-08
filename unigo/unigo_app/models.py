from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


# ============================================
# 대화 관련 모델
# ============================================

class Conversation(models.Model):
    """
    대화 세션 모델
    
    로그인 사용자와 비로그인 사용자 모두 지원:
    - 로그인 사용자: user 필드 사용
    - 비로그인 사용자: session_id 필드 사용
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='conversations',
        help_text="로그인한 사용자 (비로그인 시 null)"
    )
    session_id = models.CharField(
        max_length=255, 
        unique=True,
        help_text="세션 ID (비로그인 사용자 식별용)"
    )
    title = models.CharField(
        max_length=255, 
        default="새 대화",
        help_text="대화 제목 (첫 메시지에서 자동 생성)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.title}"
        return f"Guest ({self.session_id[:8]}) - {self.title}"
    
    def get_message_count(self):
        """대화의 메시지 개수"""
        return self.messages.count()
    
    def get_last_message(self):
        """마지막 메시지"""
        return self.messages.last()


class Message(models.Model):
    """
    개별 메시지 모델
    
    대화 세션 내의 각 메시지를 저장
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES,
        help_text="메시지 역할 (user/assistant/system)"
    )
    content = models.TextField(help_text="메시지 내용")
    metadata = models.JSONField(
        null=True, 
        blank=True,
        help_text="추가 정보 (tool 호출, 검색 결과 등)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
        ]
    
    def __str__(self):
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"{self.role}: {content_preview}"


class MajorRecommendation(models.Model):
    """
    전공 추천 결과 모델
    
    온보딩 질문 답변 기반 전공 추천 결과 저장
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='major_recommendations'
    )
    session_id = models.CharField(
        max_length=255,
        help_text="세션 ID (비로그인 사용자 식별용)"
    )
    onboarding_answers = models.JSONField(
        help_text="온보딩 질문 답변 (subjects, interests, desired_salary, preferred_majors)"
    )
    recommended_majors = models.JSONField(
        help_text="추천된 전공 목록 및 점수"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        if self.user:
            return f"{self.user.username} - 전공 추천 ({self.created_at.strftime('%Y-%m-%d')})"
        return f"Guest ({self.session_id[:8]}) - 전공 추천 ({self.created_at.strftime('%Y-%m-%d')})"


# ============================================
# 전공 정보 모델 (backend/data 마이그레이션용)
# ============================================

class Major(models.Model):
    """
    전공 정보 모델
    
    backend/data/major_detail.json 데이터를 DB로 마이그레이션
    """
    name = models.CharField(
        max_length=255, 
        unique=True,
        help_text="전공명"
    )
    cluster = models.CharField(
        max_length=100,
        help_text="계열 (예: 공학계열, 인문계열)"
    )
    summary = models.TextField(
        help_text="전공 요약 설명"
    )
    interest = models.TextField(
        help_text="관심사 및 적성"
    )
    property = models.TextField(
        help_text="전공 특성"
    )
    salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True,
        blank=True,
        help_text="평균 연봉 (만원)"
    )
    employment_rate = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="취업률"
    )
    department = models.TextField(
        help_text="관련 학과명 (쉼표로 구분)"
    )
    
    # JSON 필드
    relate_subjects = models.JSONField(
        help_text="관련 과목 정보"
    )
    career_activities = models.JSONField(
        null=True,
        blank=True,
        help_text="진로 활동"
    )
    jobs = models.TextField(
        help_text="진출 직업 (쉼표로 구분)"
    )
    qualifications = models.TextField(
        null=True,
        blank=True,
        help_text="관련 자격증 (쉼표로 구분)"
    )
    enter_fields = models.JSONField(
        null=True,
        blank=True,
        help_text="진출 분야 정보"
    )
    main_subjects = models.JSONField(
        null=True,
        blank=True,
        help_text="주요 과목 정보"
    )
    chart_data = models.JSONField(
        null=True,
        blank=True,
        help_text="통계 데이터 (성별, 분야, 연봉, 만족도 등)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['cluster']),
        ]
    
    def __str__(self):
        return self.name


class University(models.Model):
    """
    대학 정보 모델
    """
    name = models.CharField(
        max_length=255,
        help_text="대학명"
    )
    area = models.CharField(
        max_length=100,
        help_text="지역"
    )
    campus_name = models.CharField(
        max_length=255,
        help_text="캠퍼스명"
    )
    school_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        help_text="대학 홈페이지 URL"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name', 'campus_name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['area']),
        ]
        unique_together = ['name', 'campus_name']
    
    def __str__(self):
        if self.campus_name != "제1캠퍼스":
            return f"{self.name} ({self.campus_name})"
        return self.name


class MajorUniversity(models.Model):
    """
    전공-대학 연결 모델
    
    특정 대학에서 개설한 전공 정보
    """
    major = models.ForeignKey(
        Major,
        on_delete=models.CASCADE,
        related_name='universities'
    )
    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name='majors'
    )
    major_name_at_university = models.CharField(
        max_length=255,
        help_text="해당 대학에서의 전공명 (대학마다 다를 수 있음)"
    )
    
    class Meta:
        unique_together = ['major', 'university']
        indexes = [
            models.Index(fields=['major']),
            models.Index(fields=['university']),
        ]
    
    def __str__(self):
        return f"{self.major.name} @ {self.university.name}"
