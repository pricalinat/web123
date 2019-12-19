from django.http import HttpResponse
from django.shortcuts import render
import datetime
from django.conf import settings

from django.shortcuts import render
from django.shortcuts import redirect

from . import models
from . import forms
from challenges.models import Challenges
from challenges.views import PassInsideView
from accounts import models as accounts_models


# Create your views here.
def in_exam(request):
    user = accounts_models.User.objects.get(id=request.session['user_id'])
    if models.Exam.objects.filter(user=user).exists():
        return True
    else:
        return False


def correct(request, point):
    user = accounts_models.User.objects.get(id=request.session['user_id'])
    e = models.Exam.objects.get(user=user)
    e.point = e.point + point
    e.save()


def rest_time(request):
    user = accounts_models.User.objects.get(id=request.session['user_id'])
    e = models.Exam.objects.get(user=user)
    now = datetime.datetime.now()
    # now = now.replace(tzinfo=pytz.timezone('Asia/Shanghai'))
    start = e.start_time
    start = start.replace(tzinfo=None)
    time = 115200 - (now - start).seconds
    return time


def set_exam(request):
    if not request.session.get('is_login', None):
        return redirect('/accounts/login/')
    if in_exam(request):
        return redirect('/exam/examination/')
    if request.method == 'POST':
        diff = request.POST.get('diff')
        p_type = request.POST.get('p_type')
        user = models.User.objects.get(id=request.session['user_id'])
        problems = []
        origin_challenge = models.Challenges.objects.all()
        challenge = []  # 用户没做的题
        for o_c in origin_challenge:
            if not o_c.solver.filter(id=request.session['user_id']).exists():
                challenge.append(o_c)
        if diff == 'low':
            low_p = []
            for c in challenge:
                if c.point < 100:
                    low_p.append(c)
            if len(low_p) >= 4:
                if p_type == 'all':
                    problems = low_p[0:4].copy()
                else:
                    for c in low_p:
                        if str(c.category) == p_type:
                            problems.append(c)
                    if len(problems) >= 4:
                        problems = problems[0:4]
                    else:
                        message = '题库中所剩符合要求的题目较少，无法生成试卷'
                        return render(request, 'set_exam.html', locals())
            else:
                message = '题库中所剩低难度的题目较少，无法生成试卷'
                return render(request, 'set_exam.html', locals())

        if diff == 'medium':
            medium_p = []
            for c in challenge:
                if c.point < 200 and c.point >= 100:
                    medium_p.append(c)
            if len(medium_p) >= 4:
                if p_type == 'all':
                    problems = medium_p[0:4].copy()
                else:
                    for c in medium_p:
                        if str(c.category) == p_type:
                            problems.append(c)
                    if len(problems) >= 4:
                        problems = problems[0:4]
                    else:
                        message = '题库中所剩符合要求的题目较少，无法生成试卷'
                        return render(request, 'set_exam.html', locals())
            else:
                message = '题库中所剩中等难度的题目较少，无法生成试卷'
                return render(request, 'set_exam.html', locals())

        if diff == 'high':
            high_p = []
            for c in challenge:
                if c.point >= 200:
                    high_p.append(c)
            if len(high_p) >= 4:
                if p_type == 'all':
                    problems = high_p[0:4].copy()
                else:
                    for c in high_p:
                        if str(c.category) == p_type:
                            problems.append(c)
                    if len(problems) >= 4:
                        problems = problems[0:4]
                    else:
                        message = '题库中所剩符合要求的题目较少，无法生成试卷'
                        return render(request, 'set_exam.html', locals())
            else:
                message = '题库中所剩高难度的题目较少，无法生成试卷'
                return render(request, 'set_exam.html', locals())

        if diff == 'all':
            if len(challenge) >= 4:
                if p_type == 'all':
                    problems = challenge[0:4].copy()
                else:
                    for c in challenge:
                        if str(c.category) == p_type:
                            problems.append(c)
                    if len(problems) >= 4:
                        problems = problems[0:4]
                    else:
                        message = '题库中所剩符合要求的题目较少，无法生成试卷'
                        return render(request, 'set_exam.html', locals())
            else:
                message = '题库中所剩符合要求的题目较少，无法生成试卷'
                return render(request, 'set_exam.html', locals())
        e = models.Exam.objects.create(user=user)
        full_marks = 0
        for p in problems:
            full_marks += p.point
            e.problems.add(p)
        e.full_marks = full_marks
        e.start_time = datetime.datetime.now()
        e.save()
        request.session['exam'] = 1
        return redirect('/exam/examination/')

    return render(request, 'set_exam.html', locals())


def examination(request):
    if not request.session.get('is_login', None):
        return redirect('/accounts/login/')
    if not in_exam(request):
        return redirect('/exam/set_exam/')
    if rest_time(request)<0:
        return redirect('/exam/end_exam/')
    current_id = request.session['user_id']
    current_user = accounts_models.User.objects.get(id=current_id)
    e = models.Exam.objects.get(user=current_user)
    challenge = e.problems.all()
    problems = []  # 加工后的challenge
    for c in challenge:
        is_solved = 0
        is_collected = 0
        solver = c.solver.all()
        collector = c.collector.all()
        if c.solver.filter(id=current_id).exists():
            is_solved = 1
        if c.collector.filter(id=current_id).exists():
            is_collected = 1
        p = PassInsideView(c.name, c.category, c.message, c.point, c.file, c.flag, c.id, c.scene, is_solved,
                           is_collected)
        problems.append(p)

    # now = datetime.datetime.now()
    # # now = now.replace(tzinfo=pytz.timezone('Asia/Shanghai'))
    # start = e.start_time
    # start = start.replace(tzinfo=None)
    # time = 115200-(now-start).seconds
    # time = 3
    time = rest_time(request)
    return render(request, 'examination.html', locals())


def end_exam(request):
    if not request.session.get('is_login', None):
        return redirect('/accounts/login/')
    if not in_exam(request):
        return redirect('/exam/set_exam/')
    user = accounts_models.User.objects.get(id=request.session['user_id'])
    e = models.Exam.objects.get(user=user)
    if rest_time(request) > 0:
        point = e.point
        problems = e.problems.all()
        num = 0
        for p in problems:
            if p.solver.filter(id=request.session['user_id']).exists():
                num += 1
        addition = 0
        if point >= e.full_marks*0.7:
            addition = point*0.2
        user.point += addition
        user.save()
        e.delete()
        return render(request,'end_exam.html',locals())
    else:
        response = '提交超时'
        e.delete()
        return HttpResponse(response)
