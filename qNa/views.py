from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from .models import Qna, Answer

User = get_user_model()


@login_required
def qna_my_list(request):
    sent_list = Qna.objects.filter(sender=request.user).order_by("-id")
    received_list = Qna.objects.filter(receiver=request.user).order_by("-id")

    return render(request, 'qna_my.html', {
        'sent_list': sent_list,
        'received_list': received_list,
    })

def qna_user_list(request, user_id):
    # 자기 자신이면 마이페이지로
    if request.user.is_authenticated and request.user.id == user_id:
        return redirect('qna:my_list')

    target_user = get_object_or_404(User, id=user_id)

    # 답변이 하나라도 달린 질문만 공개
    received_list = (
        Qna.objects.filter(receiver=target_user, answers__isnull=False)
        .distinct()
        .order_by("-id")
    )

    return render(request, 'qna_user.html', {
        'target_user': target_user,
        'received_list': received_list,
    })

@login_required
def qna_answer_list(request):
    # 원래 의도가 "답변할 리스트"면 unanswered만 보여주는 게 보통
    qnas = Qna.objects.filter(answers__isnull=True).order_by("-id")
    return render(request, 'qna_answer_list.html', {'qnas': qnas})


@login_required
def qna_write(request):
    receiver_id = request.GET.get('receiver')
    if not receiver_id:
        return HttpResponseBadRequest("잘못된 접근입니다.")

    receiver = get_object_or_404(User, id=receiver_id)

    # 자기 자신에게 질문 금지
    if receiver == request.user:
        return HttpResponseForbidden("자기 자신에게는 질문할 수 없습니다.")

    return render(request, 'qna_write.html', {
        'sender': request.user,
        'receiver': receiver,
    })

@login_required
@require_POST
def qna_submit(request):
    title = (request.POST.get('title') or "").strip()
    content = (request.POST.get('content') or "").strip()
    receiver_id = request.POST.get('receiver_id')

    if not title or not content or not receiver_id:
        return HttpResponseBadRequest("필수값이 누락되었습니다.")

    receiver = get_object_or_404(User, id=receiver_id)

    if receiver == request.user:
        return HttpResponseForbidden("자기 자신에게는 질문할 수 없습니다.")

    qna = Qna.objects.create(
        title=title,
        content=content,
        sender=request.user,
        receiver=receiver
    )

    return redirect('qna:detail', qna_id=qna.id)

def qna_detail(request, qna_id):
    print("qna check")
    qna = get_object_or_404(Qna, pk=qna_id)
    user = request.user

    has_answer = qna.answers.exists()
    if not has_answer:
        if not user.is_authenticated or (user != qna.receiver and user != qna.sender):
            return HttpResponseForbidden("아직 답변이 달리지 않은 질문입니다.")

    answers = qna.answers.all().order_by("id")

    can_answer = (
        user.is_authenticated
        and user == qna.receiver          
        and not has_answer               
    )

    return render(request, 'qna_detail.html', {
        'qna': qna,
        'answers': answers,
        'has_answer': has_answer,
        'can_answer': can_answer,
    })

@login_required
@require_POST
def answer_submit(request, qna_id):
    qna = get_object_or_404(Qna, id=qna_id)
    content = (request.POST.get('content') or "").strip()

    if not content:
        return HttpResponseBadRequest("답변 내용을 입력해주세요.")

    user = request.user

    if user != qna.receiver:
        return HttpResponseForbidden("답변 권한이 없습니다.")

    if qna.answers.exists():
        return HttpResponseForbidden("이미 답변이 등록된 질문입니다.")

    Answer.objects.create(
        qna=qna,
        content=content,
        user=user,
        display_name=getattr(user, "username", "익명")  
    )

    return redirect('qna:detail', qna_id=qna.id)

@login_required
@require_GET
def my_qna_api(request):
    sent_qs = (
        Qna.objects.filter(sender=request.user)
        .select_related("receiver")
        .order_by("-id")
    )
    received_qs = (
        Qna.objects.filter(receiver=request.user)
        .select_related("sender")
        .order_by("-id")
    )

    sent = [
        {
            "id": q.id,
            "title": q.title,
            "content": q.content,
            "created_at": q.created_at.isoformat(),
            "receiver_id": q.receiver_id,
            "receiver_username": getattr(q.receiver, "username", None),
        }
        for q in sent_qs
    ]

    received = [
        {
            "id": q.id,
            "title": q.title,
            "content": q.content,
            "created_at": q.created_at.isoformat(),
            "sender_id": q.sender_id,
            "sender_username": getattr(q.sender, "username", None),
        }
        for q in received_qs
    ]

    return JsonResponse({"sent": sent, "received": received})