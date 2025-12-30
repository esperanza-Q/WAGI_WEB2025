# --- 통합 검색 뷰 (모집/취업 게시판) ---
# from recruit.models import Recruit
# from career.models import PassPost
# from django.db.models import Q
# import re
#
# def integrated_search(request):
#     q = request.GET.get('q', '').strip()
#     category = request.GET.get('category', '').strip()
#
#     recruit_results = []
#     passpost_results = []
#
#     # 모집 게시판 검색
#     if q or category:
#         recruit_q = Q()
#         if q:
#             words = [w.strip() for w in re.split(r'[ ,]+', q) if w.strip()]
#             for word in words:
#                 recruit_q |= Q(title__icontains=word) | Q(body__icontains=word)
#         if category:
#             recruit_q &= Q(category__category_name=category)
#         recruit_q &= Q(is_recruiting=True)
#         recruit_results = Recruit.objects.filter(recruit_q).distinct()
#     else:
#         recruit_results = Recruit.objects.filter(is_recruiting=True)
#
#     # 취업/합격 후기 게시판 검색
#     if q or category:
#         passpost_q = Q()
#         if q:
#             words = [w.strip() for w in re.split(r'[ ,]+', q) if w.strip()]
#             for word in words:
#                 passpost_q |= Q(title__icontains=word) | Q(content__icontains=word)
#         if category:
#             passpost_q &= Q(category__category_name=category)
#         passpost_results = PassPost.objects.filter(passpost_q).distinct()
#     else:
#         passpost_results = PassPost.objects.all()
#
#     context = {
#         'recruit_results': recruit_results,
#         'passpost_results': passpost_results,
#         'q_query': q,
#         'category': category,
#     }
#     return render(request, 'b_search_integrated.html', context)
