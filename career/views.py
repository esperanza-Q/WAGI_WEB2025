# career/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django import forms

from .models import RoadmapEntry


# --------- 폼 정의 (모델 기반) ---------
class RoadmapEntryForm(forms.ModelForm):
    class Meta:
        model = RoadmapEntry
        fields = [
            'title',
            'category',
            'date',
            'period_text',
            'description',
            'image',
            'attachment',
            'tags',
        ]


# ---------------------------------------
#  비로그인 테스트용 VIEW 전체 버전
# ---------------------------------------

def roadmap_list(request):
    """
    익명 사용자도 접속 가능.
    로그인한 경우 → 본인 글만
    익명인 경우 → 빈 리스트(오류 방지)
    """
    if request.user.is_authenticated:
        entries = RoadmapEntry.objects.filter(user=request.user).order_by('-date')
    else:
        # 테스트용: 아무 글 없게
        entries = RoadmapEntry.objects.none()

    grouped = {}
    for e in entries:
        grouped.setdefault(e.year, []).append(e)

    return render(request, 'career/b_roadmap_list.html', {
        'entries': entries,
        'grouped_entries': grouped
    })



def roadmap_detail(request, pk):
    """
    테스트용: user 제한 없이 로드맵 항목 detail 열람 가능.
    (원래는 user=request.user로 제한하지만 테스트라 제거)
    """
    entry = get_object_or_404(RoadmapEntry, pk=pk)
    return render(request, 'career/b_roadmap_detail.html', {'entry': entry})



def roadmap_create(request):
    """
    비로그인 테스트용:
      - 익명일 때도 페이지는 뜸
      - POST 시 실제 저장은 못 하게 처리 (user가 없기 때문)
    """
    if request.method == 'POST':
        form = RoadmapEntryForm(request.POST, request.FILES)

        if form.is_valid():
            if request.user.is_authenticated:
                # 로그인한 경우에만 실제 저장
                roadmap = form.save(commit=False)
                roadmap.user = request.user
                roadmap.save()
                return redirect('career:roadmap_list')
            else:
                # 익명일 때는 저장 대신 메시지만 띄우고 리다이렉트
                print("익명 사용자: 저장 생략 (테스트 모드)")
                return redirect('career:roadmap_list')
    else:
        form = RoadmapEntryForm()

    return render(request, 'career/b_roadmap_form.html', {'form': form})



def roadmap_update(request, pk):
    """
    비로그인 테스트용:
      - 익명 사용자는 수정 페이지는 열리지만 저장은 불가
    """
    # 원래는 user 검증해야 하지만 테스트라 제거
    entry = get_object_or_404(RoadmapEntry, pk=pk)

    if request.method == 'POST':
        form = RoadmapEntryForm(request.POST, request.FILES, instance=entry)

        if form.is_valid():
            if request.user.is_authenticated:
                form.save()
                return redirect('career:roadmap_detail', pk=entry.pk)
            else:
                print("익명 사용자: 수정 저장 생략 (테스트 모드)")
                return redirect('career:roadmap_detail', pk=entry.pk)
    else:
        form = RoadmapEntryForm(instance=entry)

    return render(request, 'career/b_roadmap_form.html', {
        'form': form,
        'entry': entry
    })



def roadmap_delete(request, pk):
    """
    비로그인 테스트용:
      - 삭제 페이지는 열리지만
      - 익명 사용자는 실제 삭제 불가
    """
    entry = get_object_or_404(RoadmapEntry, pk=pk)

    if request.method == 'POST':
        if request.user.is_authenticated:
            entry.delete()
        else:
            print("익명 사용자: 삭제 생략 (테스트 모드)")

        return redirect('career:roadmap_list')

    return render(request, 'career/b_roadmap_confirm_delete.html', {
        'entry': entry
    })
