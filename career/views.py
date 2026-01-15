from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404

from .models import RoadmapEntry


@login_required
def roadmap_home(request):
    # ✅ date는 문자열이라 안정 정렬은 -id 기준
    entries = RoadmapEntry.objects.filter(user=request.user).order_by("-id")

    # ✅ 시작 연도 기준 그룹핑 (models.py의 @property year 사용)
    grouped = {}
    for e in entries:
        grouped.setdefault(e.year, []).append(e)

    return render(request, "myroadmaphome.html", {
        "entries": entries,
        "grouped_entries": grouped,
    })


@login_required
def roadmap_detail_front(request, pk):
    entry = get_object_or_404(RoadmapEntry, pk=pk, user=request.user)
    return render(request, "myroadmap-detail.html", {"entry": entry})


@login_required
def roadmap_create_front(request):
    if request.method == "POST":
        # ✅ 텍스트 기반으로만 받음 (프론트와 계약 일치)
        title = request.POST.get("title", "").strip()
        category = request.POST.get("category", "").strip()
        date = request.POST.get("date", "").strip()  # ✅ 기간 문자열
        description = request.POST.get("description", "").strip()

        # ✅ date는 NOT NULL 이므로 최소한 빈 문자열 방지
        if not date:
            date = "미입력"

        entry = RoadmapEntry(
            user=request.user,
            title=title,
            category=category,
            date=date,  # ✅ 문자열 그대로 저장
            description=description,
        )

        # ✅ 파일 업로드 (1차 연동: 1개만 저장)
        files = request.FILES.getlist("files")
        if files:
            first = files[0]
            if first.content_type and first.content_type.startswith("image/"):
                entry.image = first
            else:
                entry.attachment = first

        entry.save()
        return redirect("career:roadmap_home")

    return render(request, "myroadmap-post.html")


@login_required
def roadmap_update_front(request, pk):
    entry = get_object_or_404(RoadmapEntry, pk=pk, user=request.user)

    if request.method == "POST":
        entry.title = request.POST.get("title", entry.title).strip()
        entry.category = request.POST.get("category", entry.category).strip()

        # ✅ 문자열 date 그대로 갱신
        date = request.POST.get("date", "").strip()
        if date:
            entry.date = date

        entry.description = request.POST.get("description", entry.description).strip()

        files = request.FILES.getlist("files")
        if files:
            first = files[0]
            if first.content_type and first.content_type.startswith("image/"):
                entry.image = first
            else:
                entry.attachment = first

        entry.save()
        return redirect("career:roadmap_detail_front", pk=entry.pk)

    return render(request, "myroadmap-edit.html", {"entry": entry})


@login_required
def roadmap_delete(request, pk):
    entry = get_object_or_404(RoadmapEntry, pk=pk, user=request.user)

    if request.method == "POST":
        entry.delete()
        return redirect("career:roadmap_home")

    return redirect("career:roadmap_detail_front", pk=entry.pk)


@login_required
def roadmap_detail_query(request):
    """
    /career/myroadmap-detail.html?id=13 형태를 받아서
    기존 pk 기반 상세 페이지로 리다이렉트한다.
    """
    pk = request.GET.get("id")
    if not pk or not pk.isdigit():
        raise Http404("Invalid id")

    return redirect("career:roadmap_detail_front", pk=int(pk))