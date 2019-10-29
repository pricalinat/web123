from django.shortcuts import render
from django.shortcuts import redirect

from . import models
from . import forms
from challenges.models import Challenges
import hashlib


# Create your views here.


def hash_code(s, salt='myctf'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()


def index(request):
    # if not request.session.get('is_login', None):
    #     return redirect('/accounts/login/')
    return render(request, 'accounts/index.html')


def login(request):
    if request.session.get('is_login', None):  # 不允许重复登录
        return redirect('/accounts/index/')
    if request.method == 'POST':
        login_form = forms.UserForm(request.POST)
        message = '请检查填写的内容！'
        if login_form.is_valid():
            student_id = login_form.cleaned_data.get('student_id')
            password = login_form.cleaned_data.get('password')

            try:
                user = models.User.objects.get(student_id=student_id)
            except:
                message = '用户不存在！'
                return render(request, 'accounts/login.html', locals())

            if user.password == hash_code(password):
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                request.session['student_id'] = user.student_id
                try:
                    request.session['team_name'] = user.team.team_name
                    if user.name == user.team.team_leader:
                        request.session['is_leader'] = 1
                    else:
                        request.session['is_leader'] = 0
                except:
                    request.session['team_name'] = "暂无"
                    request.session['is_leader'] = 0
                return redirect('/accounts/index/')
            else:
                message = '密码不正确！'
                return render(request, 'accounts/login.html', locals())
        else:
            return render(request, 'accounts/login.html', locals())

    login_form = forms.UserForm()
    return render(request, 'accounts/login.html', locals())


def register(request):
    if request.session.get('is_login', None):
        return redirect('/accounts/index/')

    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():
            input_student_id = register_form.cleaned_data.get('student_id')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            # email = register_form.cleaned_data.get('email')
            # sex = register_form.cleaned_data.get('sex')

            try:
                models.BaseInfo.objects.get(baseId=input_student_id)
            except:
                message = '输入的学号不合法'
                return render(request, 'accounts/register.html', locals())
            if len(str(password1)) < 6:
                message = '密码长度不得小于6位啊亲'
                return render(request, 'accounts/register.html', locals())
            elif password1 != password2:
                message = '两次输入的密码不同！'
                return render(request, 'accounts/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(student_id=input_student_id)
                if same_name_user:
                    message = '用户已经存在'
                    return render(request, 'accounts/register.html', locals())
                # same_email_user = models.User.objects.filter(email=email)
                # if same_email_user:
                #     message = '该邮箱已经被注册了！'
                #     return render(request, 'accounts/register.html', locals())

                base_user = models.BaseInfo.objects.get(baseId=input_student_id)
                username = base_user.baseName

                new_user = models.User()
                new_user.student_id = input_student_id
                new_user.name = username
                new_user.password = hash_code(password1)
                # new_user.email = email
                new_user.save()

                # code = make_confirm_string(new_user)
                # send_email(email, code) #把带e-mail的去掉，验证去掉（68）

                # message = '请前往邮箱进行确认！'
                # return render(request, 'accounts/confirm.html', locals())
                # message = '注册成功'
                return redirect("/accounts/login/")
        else:
            return render(request, 'accounts/register.html', locals())
    register_form = forms.RegisterForm()
    return render(request, 'accounts/register.html', locals())


def logout(request):
    if not request.session.get('is_login', None):
        return redirect('/accounts/login/')

    request.session.flush()
    # del request.session['is_login']
    return redirect("/accounts/login/")


def profile(request):
    if not request.session.get('is_login', None):
        return redirect('/accounts/login/')
    try:    # 更新战队信息
        user = models.User.objects.get(id=request.session['user_id'])
        request.session['team_name'] = user.team.team_name
        if user.name == user.team.team_leader:
            request.session['is_leader'] = 1
        else:
            request.session['is_leader'] = 0
    except:
        request.session['team_name'] = "暂无"
        request.session['is_leader'] = 0
    challenges = Challenges.objects.all()
    solved=[]
    for challenge in challenges:
        solvers = list(challenge.solver.all())
        if (user in solvers):
            solved.append(challenge)
    length = len(solved)
    # point = 0   # 可以封装成方法
    # for challenge in challenges:
    #     solvers = list(challenge.solver.all())
    #     if (user in solvers):
    #         point += challenge.point
    return render(request,'accounts/profile/profile.html',locals())


def change_pwd(request):
    if not request.session.get('is_login', None):
        return redirect('/accounts/login/')
    if request.method == 'POST':
        update_form = forms.UpdateForm(request.POST)
        message = "请检查填写的内容！"
        if update_form.is_valid():
            origin_password = update_form.cleaned_data.get('origin_password')
            new_password = update_form.cleaned_data.get('new_password')
            confirm_password = update_form.cleaned_data.get('confirm_password')

            user = models.User.objects.get(id=request.session['user_id'])

            if not user.password == hash_code(origin_password):
                message = '原密码不正确！'
                return render(request, 'accounts/profile/change_pwd.html', locals())
            if len(str(new_password)) < 6:
                message = '密码长度不得小于6位啊亲'
                return render(request, 'accounts/profile/change_pwd.html', locals())
            elif new_password != confirm_password:
                message = '两次输入的密码不同！'
                return render(request, 'accounts/profile/change_pwd.html', locals())

            user.password = hash_code(new_password)
            user.save()
            message = '修改成功！'
            return render(request, 'accounts/profile/change_pwd.html', locals())

        else:
            return render(request, 'accounts/profile/change_pwd.html', locals())
    update_form = forms.UpdateForm()
    return render(request, 'accounts/profile/change_pwd.html',locals())


def fun(request):
    return render(request,'accounts/fun.html')
