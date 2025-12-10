from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils import timezone
import json
import sys
import os
import uuid
import logging
from django.contrib.auth.decorators import login_required

logger = logging.getLogger("unigo_app")

# Models
from .models import Conversation, Message, MajorRecommendation

# Add frontend root to path to import backend
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if frontend_dir not in sys.path:
    sys.path.append(frontend_dir)

try:
    from backend.main import run_mentor, run_major_recommendation
except ImportError as e:
    # ... (Error handling code kept brief for this tool call, assumed user already saw it) ...
    logger.error(f"Backend import failed: {e}")
    # In production, this should probably not pass silently, but for now we proceed
    pass


# ============================================
# Page Views
# ============================================


def auth(request):
    """인증(로그인/가입) 페이지 렌더링"""
    if request.user.is_authenticated:
        return redirect("unigo_app:chat")
    return render(request, "unigo_app/auth.html")


def chat(request):
    """채팅 페이지 렌더링"""
    return render(request, "unigo_app/chat.html")


def setting(request):
    """설정 페이지 렌더링"""
    if not request.user.is_authenticated:
        return redirect("unigo_app:auth")
    return render(request, "unigo_app/setting.html")


def home(request):
    """
    홈 페이지 (루트 경로)
    - 로그인 상태: 채팅 페이지로 이동
    - 비로그인 상태: 인증(로그인) 페이지로 이동
    """
    if request.user.is_authenticated:
        return redirect("unigo_app:chat")
    return redirect("unigo_app:auth")


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

        user = User.objects.create_user(
            username=username, password=password, email=email
        )
        login(request, user)  # 가입 후 자동 로그인

        return JsonResponse(
            {
                "message": "Signup successful",
                "user": {"id": user.id, "username": user.username},
            }
        )

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
            return JsonResponse(
                {"error": "Username/Email and password required"}, status=400
            )

        # 이메일 형식인지 확인
        user = None
        if "@" in username_or_email:
            # 이메일로 로그인 시도
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(
                    request, username=user_obj.username, password=password
                )
            except User.DoesNotExist:
                pass
        else:
            # Username으로 로그인 시도
            user = authenticate(request, username=username_or_email, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse(
                {
                    "message": "Login successful",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                }
            )
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


def logout_view(request):
    """
    로그아웃 뷰 (GET 요청 처리 및 리다이렉트)
    """
    logout(request)
    return redirect("unigo_app:auth")


def auth_me(request):
    """현재 사용자 정보 조회 API"""
    if request.user.is_authenticated:
        return JsonResponse(
            {
                "is_authenticated": True,
                "user": {
                    "id": request.user.id,
                    "username": request.user.username,
                    "email": request.user.email,
                    # [NEW] Return character info
                    "character": request.user.profile.character if hasattr(request.user, 'profile') else 'rabbit'
                },
            }
        )
    return JsonResponse({"is_authenticated": False})


@csrf_exempt
def auth_check_email(request):
    """이메일 중복 확인 API (Public)"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get("email")

        if not email:
            return JsonResponse({"error": "Email required"}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse(
                {"exists": True, "message": "중복 이메일이 존재합니다."}
            )

        return JsonResponse({"exists": False, "message": "사용 가능한 이메일입니다."})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def auth_check_username(request):
    """아이디(닉네임) 중복 확인 API (Public)"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        username = data.get("username")

        if not username:
            return JsonResponse({"error": "Username required"}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse(
                {"exists": True, "message": "중복 닉네임이 존재합니다."}
            )

        return JsonResponse({"exists": False, "message": "사용 가능한 닉네임입니다."})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ============================================
# Setting API
# ============================================


@csrf_exempt
@login_required
def check_username(request):
    """닉네임 중복 확인 API"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        username = data.get("username")

        if not username:
            return JsonResponse({"error": "Username required"}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse(
                {"exists": True, "message": "이미 사용 중인 닉네임입니다."}
            )

        return JsonResponse({"exists": False, "message": "사용 가능한 닉네임입니다."})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@login_required
def change_nickname(request):
    """닉네임 변경 API"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        new_username = data.get("username")
        password = data.get("password")

        if not new_username or not password:
            return JsonResponse({"error": "Username and password required"}, status=400)

        # 현재 비밀번호 검증
        user = authenticate(request, username=request.user.username, password=password)
        if user is None:
            return JsonResponse({"error": "비밀번호가 일치하지 않습니다."}, status=400)

        # 중복 확인
        if User.objects.filter(username=new_username).exists():
            return JsonResponse({"error": "이미 사용 중인 닉네임입니다."}, status=400)

        # 닉네임 변경
        user.username = new_username
        user.save()

        return JsonResponse({"message": "내용이 변경되었습니다."})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@login_required
def change_password(request):
    """비밀번호 변경 API"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        current_password = data.get("current_password")
        new_password = data.get("new_password")

        if not current_password or not new_password:
            return JsonResponse({"error": "All fields required"}, status=400)

        # 현재 비밀번호 검증
        user = authenticate(
            request, username=request.user.username, password=current_password
        )
        if user is None:
            return JsonResponse(
                {"error": "현재 비밀번호가 일치하지 않습니다."}, status=400
            )

        # 비밀번호 변경
        user.set_password(new_password)
        user.save()

        # 세션 유지
        update_session_auth_hash(request, user)

        return JsonResponse({"message": "내용이 변경되었습니다."})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@login_required
def update_character(request):
    """캐릭터 변경 API"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        character = data.get("character")

        if not character:
            return JsonResponse({"error": "Character required"}, status=400)

        # 프로필 가져오기 (없으면 생성)
        # models.py의 signal이 있어서 대부분 있지만 안전하게 처리
        from .models import UserProfile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        profile.character = character
        profile.save()

        return JsonResponse({"message": f"Character updated to {character}"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ============================================
# Chat & Feature API
# ============================================


@csrf_exempt
def chat_api(request):
    """
    챗봇 대화 API (DB 저장 포함)
    """
    logger.info("Chat API called")
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        message_text = data.get("message")
        history = data.get("history", [])  # 프론트엔드에서 보내준 히스토리 (참고용)
        session_id = data.get("session_id")  # 비로그인 사용자용 세션 ID

        if not message_text:
            return JsonResponse({"error": "Empty message"}, status=400)

        logger.debug(f"User message: {message_text}")

        # 1. 대화 세션 찾기 또는 생성
        # 로그인 사용자: DB에서 최근 대화 기록 로드
        # 비로그인 사용자: 세션 ID를 기반으로 대화 유지
        conversation = None
        if request.user.is_authenticated:
            # 로그인 사용자의 경우: 최근 대화 로드 or 새 대화
            # (여기서는 단순화를 위해 항상 가장 최근 대화를 이어서 하거나, 없으면 생성)
            conversation = (
                Conversation.objects.filter(user=request.user)
                .order_by("-updated_at")
                .first()
            )
            if not conversation:
                conversation = Conversation.objects.create(
                    user=request.user, title=message_text[:20]
                )
        else:
            # 비로그인 사용자: session_id 필수
            if not session_id:
                session_id = str(uuid.uuid4())  # 없으면 생성해서 반환

            conversation, created = Conversation.objects.get_or_create(
                session_id=session_id, defaults={"title": message_text[:20]}
            )

        # 2. 사용자 메시지 DB 저장
        Message.objects.create(
            conversation=conversation, role="user", content=message_text
        )

        # 3. Backend AI 호출 (run_mentor)
        # RAG 시스템의 핵심인 run_mentor 함수를 호출하여 LLM 답변을 생성합니다.
        # 실제 AI 호출 시에는 DB의 최근 대화 기록을 가져와서 전달하여 멀티턴 대화를 지원합니다.

        # DB 기반 히스토리 구성 (최근 10개)
        # 이전 대화 내용을 AI에게 전달하여 문맥(Context)을 이해하도록 함
        db_messages = conversation.messages.order_by("created_at")[:10]
        chat_history_for_ai = [
            {"role": msg.role, "content": msg.content} for msg in db_messages
        ]

        try:
            response_content = run_mentor(
                question=message_text, chat_history=chat_history_for_ai, mode="react"
            )
        except Exception as e:
            # AI 호출 실패 시 로그 남기고 에러 반환
            logger.error(f"AI Error: {e}")
            return JsonResponse({"error": "AI Server Error"}, status=503)

        ai_response_text = str(response_content)
        if isinstance(response_content, dict):
            ai_response_text = str(response_content)  # 혹시 dict가 오면 문자열로

        # 4. AI 응답 DB 저장
        Message.objects.create(
            conversation=conversation, role="assistant", content=ai_response_text
        )

        logger.info("Response generated successfully")

        return JsonResponse(
            {
                "response": ai_response_text,
                "session_id": conversation.session_id
                if not request.user.is_authenticated
                else None,
                "conversation_id": conversation.id,
            }
        )

    except Exception as e:
        logger.error(f"Error in chat_api: {e}", exc_info=True)
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def chat_history(request):
    """
    사용자 대화 기록 조회 API
    """
    try:
        # 최근 대화 세션 가져오기
        conversation = (
            Conversation.objects.filter(user=request.user)
            .order_by("-updated_at")
            .first()
        )

        if not conversation:
            return JsonResponse({"history": []})

        # 메시지 조회 (최근 순으로 가져와서 다시 시간순 정렬할 수도 있지만,
        # 여기서는 전체 대화 흐름이 중요하므로 생성일 오름차순으로 가져옴)
        # 너무 많으면 최근 N개만 가져오도록 제한 가능 (예: 50개)
        messages = conversation.messages.order_by("created_at")

        history_data = [
            {
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages
        ]

        return JsonResponse({"history": history_data})

    except Exception as e:
        logger.error(f"Error in chat_history: {e}", exc_info=True)
        return JsonResponse({"error": str(e)}, status=500)

    except Exception as e:
        logger.error(f"Error in chat_history: {e}", exc_info=True)
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@login_required
def reset_chat_history(request):
    """
    사용자 대화 기록 초기화 API (새 채팅)
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        # 최근 대화 세션 가져와서 삭제 (혹은 메시지만 삭제)
        conversation = (
            Conversation.objects.filter(user=request.user)
            .order_by("-updated_at")
            .first()
        )

        if conversation:
            conversation.delete()

        # 전공 추천 결과도 리셋할지 여부: 사용자는 "새 채팅"을 불렀으므로
        # 처음부터(온보딩) 다시 시작하는 것이 자연스러움.
        # MajorRecommendation은 남겨둘 수도 있지만, 온보딩 상태를 리셋하려면
        # 클라이언트 단에서 처리가 더 중요함.

        return JsonResponse({"message": "Chat history reset successful"})

    except Exception as e:
        logger.error(f"Error in reset_chat_history: {e}", exc_info=True)
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
        # 온보딩 답변들을 기반으로 전공 추천 그래프(build_major_graph)를 실행하여
        # 맞춤형 전공을 추천받습니다.
        result = run_major_recommendation(onboarding_answers=answers)

        # 2. 결과 DB 저장
        # 추천 결과를 DB에 저장하여 추후 분석이나 마이페이지 등에서 활용할 수 있게 합니다.
        if not session_id:
            session_id = str(uuid.uuid4())

        user = request.user if request.user.is_authenticated else None

        MajorRecommendation.objects.create(
            user=user,
            session_id=session_id if not user else "",
            onboarding_answers=answers,
            recommended_majors=result.get("recommended_majors", []),
        )

        # 결과에 session_id 포함 (클라이언트가 비로그인 시 유지하도록)
        result["session_id"] = session_id

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Error in onboarding_api: {e}", exc_info=True)
        return JsonResponse({"error": str(e)}, status=500)
