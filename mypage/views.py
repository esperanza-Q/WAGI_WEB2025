from django.shortcuts import render, redirect
from experience.models import ReviewScrap, Review
from jobTips.models import JobTipPost
from qNa.models import Qna, Answer
from accounts.models import Department


# Create your views here.
def mypage_home(request):
    if request.user.is_authenticated:
        
        received_list = Qna.objects.filter(receiver=request.user).order_by("-id")
        
        return render(request, 'myhome-received.html', {'received_list': received_list})
    else:
        return redirect('accounts:login')
    
def mypage_home_sent(request):
    sent_list = Qna.objects.filter(sender=request.user).order_by("-id")
    
    return render(request, 'myhome-sent.html', {'sent_list': sent_list})
    
def scrap_list(request, category='all'):
    experience_s = ReviewScrap.objects.filter(user_id=request.user.id)
    jobTips = JobTipPost.objects.filter(scraps=request.user).order_by('-created_at')
    
    experience = Review.objects.filter(id__in=experience_s.values_list('review_id', flat=True)).order_by('-created_at')
    # jobTips = JobTipPost.objects.filter(id__in=jobTips_s.values_list('jobtippost_id', flat=True)).order_by('-created_at')
    # jobTip = JobTipPost.objects.filter(pk=jobTip_s.jobtippost_id)
    
    scrap_post = []
    
    if category == 'experience':
        for e in experience:
            scrap_post.append([e.pk, e.title, e.user, e.created_at, 'experience'])

    elif category == 'jobTips':
        for j in jobTips:
            scrap_post.append([j.pk, j.title, j.author, j.created_at, 'jobTips'])
            
    # 모집 부분도 추가
    # elif category == 'career':
        
    else:  # all
        for e in experience:
            scrap_post.append([e.pk, e.title, e.user, e.created_at, 'experience'])
        for j in jobTips:
            scrap_post.append([j.pk, j.title, j.author, j.created_at, 'jobTips'])

        scrap_post.sort(key=lambda x: x[3], reverse=True)
        
    print('final scrap_post length:', len(scrap_post))
    print('scrap_post preview:', scrap_post[:3])
        
    context = {
        'scrap_post': scrap_post,
        'current_category': category,
    }
    
    return render(request, 'myhome-scrap.html', context)

def my_post_list(request):
    return render(request, 'myhome-post.html')

def profile_update(request):
    
    if request.method=="POST":
        nickname = request.POST['new_nickname']
        grade = request.POST['new_grade']
        dept = request.POST['new_deptSelect']
        
        print("dept 값:", dept)  # 🔍 여기
        
        user = request.user
        user.display_name = nickname
        user.grade = grade
        if dept:
            user.department = Department.objects.get(dept_id=dept)
        user.save()
        
        return redirect('mypage:home')
    else:
        return render(request, 'myhome-edit.html')