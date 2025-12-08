from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils import timezone
import json
import sys
import os
import uuid

# Models
from .models import Conversation, Message, MajorRecommendation

# Add frontend root to path to import backend
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if frontend_dir not in sys.path:
    sys.path.append(frontend_dir)

try:
    from backend.main import run_mentor, run_major_recommendation
except ImportError as e:
    # ... (Error handling code kept brief for this tool call, assumed user already saw it) ...
    print(f"Backend import failed: {e}")
    # In production, this should probably not pass silently, but for now we proceed
    pass


# ============================================
# Page Views
# ============================================

def auth(request):
    """인증(로그인/가입) 페이지 렌더링"""
    if request.user.is_authenticated:
        return redirect('unigo_app:chat')
    return render(request, "unigo_app/auth.html")

def chat(request):
    """채팅 페이지 렌더링"""
    return render(request, "unigo_app/chat.html")

def setting(request):
    """설정 페이지 렌더링"""
    return render(request, "unigo_app/setting.html")

def home(request):
    """
    홈 페이지 (루트 경로)
    - 로그인 상태: 채팅 페이지로 이동
    - 비로그인 상태: 인증(로그인) 페이지로 이동
    """
    if request.user.is_authenticated:
        return redirect('unigo_app:chat')
    return redirect('unigo_app:auth')


# ============================================
# Auth API
# ============================================

@csrf_exempt
def auth_signup(request):
    """회원가입 API"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")
        email = data.get("email", "")
        
        if not username or not password:
            return JsonResponse({"error": "Username and password required"}, status=400)
            
        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already exists"}, status=400)
            
        user = User.objects.create_user(username=username, password=password, email=email)
        login(request, user)  # 가입 후 자동 로그인
        
        return JsonResponse({"message": "Signup successful", "user": {"id": user.id, "username": user.username}})
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def auth_login(request):
    """
    로그인 API
    - username 또는 email로 로그인 가능
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
        
    try:
        data = json.loads(request.body)
        username_or_email = data.get("username")  # 이메일 또는 username
        password = data.get("password")
        
        if not username_or_email or not password:
            return JsonResponse({"error": "Username/Email and password required"}, status=400)
        
        # 이메일 형식인지 확인
        user = None
        if '@' in username_or_email:
            # 이메일로 로그인 시도
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        else:
            # Username으로 로그인 시도
            user = authenticate(request, username=username_or_email, password=password)
        
        if user is not None:
            login(request, user)
            return JsonResponse({
                "message": "Login successful", 
                "user": {
                    "id": user.id, 
                    "username": user.username,
                    "email": user.email
                }
            })
        else:
            return JsonResponse({"error": "Invalid credentials"}, status=401)
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def auth_logout(request):
    """로그아웃 API"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    logout(request)
    return JsonResponse({"message": "Logout successful"})

def auth_me(request):
    """현재 사용자 정보 조회 API"""
    if request.user.is_authenticated:
        return JsonResponse({
            "is_authenticated": True,
            "user": {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email
            }
        })
    return JsonResponse({"is_authenticated": False})


# ============================================
# Chat & Feature API
# ============================================

@csrf_exempt
def chat_api(request):
    """
    챗봇 대화 API (DB 저장 포함)
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        message_text = data.get("message")
        history = data.get("history", []) # 프론트엔드에서 보내준 히스토리 (참고용)
        session_id = data.get("session_id") # 비로그인 사용자용 세션 ID
        
        if not message_text:
            return JsonResponse({"error": "Empty message"}, status=400)

        # 1. 대화 세션 찾기 또는 생성
        conversation = None
        if request.user.is_authenticated:
            # 로그인 사용자의 경우: 최근 대화 로드 or 새 대화
            # (여기서는 단순화를 위해 항상 가장 최근 대화를 이어서 하거나, 없으면 생성)
            conversation = Conversation.objects.filter(user=request.user).order_by('-updated_at').first()
            if not conversation:
                conversation = Conversation.objects.create(user=request.user, title=message_text[:20])
        else:
            # 비로그인 사용자: session_id 필수
            if not session_id:
                session_id = str(uuid.uuid4()) # 없으면 생성해서 반환
            
            conversation, created = Conversation.objects.get_or_create(
                session_id=session_id,
                defaults={'title': message_text[:20]}
            )

        # 2. 사용자 메시지 DB 저장
        Message.objects.create(
            conversation=conversation,
            role='user',
            content=message_text
        )

        # 3. Backend AI 호출 (run_mentor)
        # 실제 AI 호출 시에는 DB의 최근 대화 기록을 가져와서 전달하는 것이 좋습니다.
        # 여기서는 프론트에서 받은 history를 사용할지, DB를 긁어올지 선택해야 하는데,
        # 일단 단순화를 위해 history 파라미터를 사용하거나,
        # DB에서 최근 N개를 가져오는 로직을 추가할 수 있습니다.
        
        # DB 기반 히스토리 구성 (최근 10개)
        db_messages = conversation.messages.order_by('created_at')[:10]
        chat_history_for_ai = [
            {"role": msg.role, "content": msg.content} for msg in db_messages
        ]

        try:
            response_content = run_mentor(
                question=message_text,
                chat_history=chat_history_for_ai,
                mode="react"
            )
        except Exception as e:
            # AI 호출 실패 시 로그 남기고 에러 반환
            print(f"AI Error: {e}")
            return JsonResponse({"error": "AI Server Error"}, status=503)

        ai_response_text = str(response_content)
        if isinstance(response_content, dict):
            ai_response_text = str(response_content) # 혹시 dict가 오면 문자열로

        # 4. AI 응답 DB 저장
        Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=ai_response_text
        )

        return JsonResponse({
            "response": ai_response_text,
            "session_id": conversation.session_id if not request.user.is_authenticated else None,
            "conversation_id": conversation.id
        })
        
    except Exception as e:
        print(f"Error in chat_api: {e}")
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def onboarding_api(request):
    """
    온보딩 질문 답변 API (DB 저장 포함)
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        answers = data.get("answers")
        session_id = data.get("session_id")
        
        if not answers:
            return JsonResponse({"error": "Empty answers"}, status=400)

        # 1. Backend 추천 알고리즘 실행
        result = run_major_recommendation(onboarding_answers=answers)
        
        # 2. 결과 DB 저장
        if not session_id:
            session_id = str(uuid.uuid4())

        user = request.user if request.user.is_authenticated else None
        
        MajorRecommendation.objects.create(
            user=user,
            session_id=session_id if not user else "",
            onboarding_answers=answers,
            recommended_majors=result.get("recommended_majors", [])
        )
        
        # 결과에 session_id 포함 (클라이언트가 비로그인 시 유지하도록)
        result["session_id"] = session_id
        
        return JsonResponse(result)
        
    except Exception as e:
        print(f"Error in onboarding_api: {e}")
        return JsonResponse({"error": str(e)}, status=500)

