from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import RoadmapEntry, RoadmapImage


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

        #파일 여러개 가능하게 수정함
        files = request.FILES.getlist("files")
        entry.save()  # ✅ 먼저 entry를 저장해야 FK로 이미지 저장 가능

        for f in files:
            if f.content_type and f.content_type.startswith("image/"):
                RoadmapImage.objects.create(entry=entry, image=f)
            else:
                entry.attachment = f
                entry.save()

        return redirect("career:roadmap_home")
    return render(request, "myroadmap-post.html")


@login_required
def roadmap_update_front(request, pk):
    entry = get_object_or_404(RoadmapEntry, pk=pk, user=request.user)

    if request.method == "POST":
        entry.title = request.POST.get("title", entry.title).strip()
        entry.category = request.POST.get("category", entry.category).strip()

        date = request.POST.get("date", "").strip()
        if date:
            entry.date = date

        entry.description = request.POST.get("description", entry.description).strip()

        files = request.FILES.getlist("files")

        # ✅ 기존 이미지 개수
        existing_image_count = entry.images.count()

        # ✅ 새로 업로드한 이미지 개수
        new_image_files = [
            f for f in files
            if f.content_type and f.content_type.startswith("image/")
        ]

        # 🔒 최대 5개 제한
        if existing_image_count + len(new_image_files) > 5:
            # 필요하면 messages 써도 됨
            return redirect("career:roadmap_edit", pk=entry.pk)

        # ✅ 파일 저장
        for f in files:
            if f.content_type and f.content_type.startswith("image/"):
                RoadmapImage.objects.create(entry=entry, image=f)
            else:
                entry.attachment = f

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
def roadmap_detail_html_redirect(request):
    """
    JS에서 오는 myroadmap-detail.html?id=xx 요청을
    공식 엔드포인트 myroadmap-detail?id=xx 로 리다이렉트
    """
    query = request.META.get("QUERY_STRING", "")
    url = "/career/myroadmap-detail"
    if query:
        url = f"{url}?{query}"
    return redirect(url)


def roadmap_detail_query(request):
    pk = request.GET.get("id")
    if not pk or not pk.isdigit():
        raise Http404("Invalid id")

    return redirect("career:roadmap_detail_front", pk=int(pk))