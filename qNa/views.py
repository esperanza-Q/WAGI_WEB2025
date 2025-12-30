from django.shortcuts import render, redirect, get_object_or_404
from .models import Qna, Answer
from django.http import HttpResponseForbidden
from django.http import HttpResponseBadRequest
from django.contrib.auth import get_user_model

User = get_user_model()

def qna_my_list(request):
    sent_list = Qna.objects.filter(sender=request.user)
    received_list = Qna.objects.filter(receiver=request.user)

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
    received_list = Qna.objects.filter(
        receiver=target_user,
        answers__isnull=False
    ).distinct()

    return render(request, 'qna_user.html', {
        'target_user': target_user,
        'received_list': received_list,
    })


def qna_answer_list(request):
    # qnas = Qna.objects.filter(answers__isnull=True)
    qnas = Qna.objects.all()
    return render(request, 'qna_answer_list.html', {'qnas': qnas})

def qna_write(request):
    receiver_id = request.GET.get('receiver')
    if not receiver_id:
        return HttpResponseBadRequest("잘못된 접근입니다.")

    receiver = get_object_or_404(User, id=receiver_id)

    sender = request.user

    return render(request, 'qna_write.html', {
        'sender': sender,
        'receiver': receiver,
    })

def qna_submit(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        receiver_id = request.POST.get('receiver_id')

        receiver = get_object_or_404(User, id=receiver_id)

        Qna.objects.create(
            title=title,
            content=content,
            sender=request.user,
            receiver=receiver
        )

        # 질문 받은 사람 QnA 페이지로 이동
        return redirect('qna:user_qna', user_id=receiver.id)

def qna_detail(request, qna_id):
    qna = get_object_or_404(Qna, pk=qna_id)
    user = request.user

    # 답변 없는 질문 접근 제한 (receiver / sender는 허용)
    if not qna.answers.exists():
        if user != qna.receiver and user != qna.sender:
            return HttpResponseForbidden("아직 답변이 달리지 않은 질문입니다.")

    return render(request, 'qna_detail.html', {
        'qna': qna,
        'answers': qna.answers.all(), 
    })


def answer_submit(request, qna_id):
    if request.method == 'POST':
        qna = get_object_or_404(Qna, id=qna_id)
        content = request.POST.get('content')

        user = request.user

        Answer.objects.create(
            qna=qna,
            content=content,
            user=user,
            display_name=user.username   # 또는 user.nickname
        )

        return redirect('qna:detail', qna_id=qna.id)

    return redirect('qna:detail', qna_id=qna_id)
