from django.contrib import admin
from .models import (
    Conversation, Message, MajorRecommendation,
    Major, University, MajorUniversity
)


# ============================================
# 대화 관련 Admin
# ============================================

class MessageInline(admin.TabularInline):
    """대화 내 메시지를 인라인으로 표시"""
    model = Message
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('role', 'content', 'created_at')


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user_display', 'title', 'message_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'session_id', 'user__username')
    readonly_fields = ('created_at', 'updated_at', 'session_id')
    inlines = [MessageInline]
    
    def get_user_display(self, obj):
        if obj.user:
            return obj.user.username
        return f"Guest ({obj.session_id[:8]})"
    get_user_display.short_description = 'User'
    
    def message_count(self, obj):
        return obj.get_message_count()
    message_count.short_description = 'Messages'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'role', 'content_preview', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('content', 'conversation__title')
    readonly_fields = ('created_at',)
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'


@admin.register(MajorRecommendation)
class MajorRecommendationAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user_display', 'get_preferred_majors', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('session_id', 'user__username')
    readonly_fields = ('created_at',)
    
    def get_user_display(self, obj):
        if obj.user:
            return obj.user.username
        return f"Guest ({obj.session_id[:8]})"
    get_user_display.short_description = 'User'
    
    def get_preferred_majors(self, obj):
        return obj.onboarding_answers.get('preferred_majors', 'N/A')
    get_preferred_majors.short_description = 'Preferred Majors'


# ============================================
# 전공 정보 Admin
# ============================================

class MajorUniversityInline(admin.TabularInline):
    """전공에 연결된 대학을 인라인으로 표시"""
    model = MajorUniversity
    extra = 0
    fields = ('university', 'major_name_at_university')


@admin.register(Major)
class MajorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'cluster', 'salary', 'employment_rate', 'university_count')
    list_filter = ('cluster',)
    search_fields = ('name', 'department', 'jobs')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [MajorUniversityInline]
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'cluster', 'department')
        }),
        ('상세 설명', {
            'fields': ('summary', 'interest', 'property')
        }),
        ('취업 정보', {
            'fields': ('salary', 'employment_rate', 'jobs', 'qualifications')
        }),
        ('교육 정보', {
            'fields': ('relate_subjects', 'main_subjects', 'enter_fields', 'career_activities')
        }),
        ('통계 데이터', {
            'fields': ('chart_data',),
            'classes': ('collapse',)
        }),
        ('메타 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def university_count(self, obj):
        return obj.universities.count()
    university_count.short_description = 'Universities'


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'campus_name', 'area', 'major_count')
    list_filter = ('area',)
    search_fields = ('name', 'area')
    readonly_fields = ('created_at', 'updated_at')
    
    def major_count(self, obj):
        return obj.majors.count()
    major_count.short_description = 'Majors'


@admin.register(MajorUniversity)
class MajorUniversityAdmin(admin.ModelAdmin):
    list_display = ('id', 'major', 'university', 'major_name_at_university')
    list_filter = ('university__area',)
    search_fields = ('major__name', 'university__name', 'major_name_at_university')

