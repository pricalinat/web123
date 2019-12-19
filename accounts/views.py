import datetime
from django.conf import settings
from django.http import HttpResponse

from django.shortcuts import render
from django.shortcuts import redirect

from . import models
from . import forms
from challenges.models import Challenges
import hashlib

from exam.views import in_exam


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
            if not user.has_confirmed:
                message = '该用户还未经过邮件确认！'
                return render(request, 'accounts/login.html', locals())

            if user.password == hash_code(password):
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                request.session['student_id'] = user.student_id
                request.session['email'] = user.email
                if in_exam(request):
                    request.session['exam'] = 1
                else:
                    request.session['exam'] = 0
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


def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.name, now)
    models.ConfirmString.objects.create(code=code, user=user, )
    return code


def send_email(email, code):
    from django.core.mail import EmailMultiAlternatives

    subject = '来自MyCTF的注册确认邮件'

    text_content = '''感谢您的注册\
                    如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！'''

    html_content = '''
                    <p>感谢注册<a href="http://{}/accounts/confirm/?code={}" target=blank>MyCTF</a>，\
                    </p>
                    <p>请点击站点链接完成注册确认！</p>
                    <p>此链接有效期为{}天！</p>
                    '''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def send_email_reset(email, code):
    from django.core.mail import EmailMultiAlternatives

    subject = '来自MyCTF的重置密码邮件'

    text_content = '''
                    如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！'''

    html_content = '''
                    <p>戳<a href="http://{}/accounts/reset/?code={}" target=blank>我</a>重置密码\
                    </p>
                    '''.format('127.0.0.1:8000', code)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


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
            email = register_form.cleaned_data.get('email')
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
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:
                    message = '该邮箱已经被注册了！'
                    return render(request, 'accounts/register.html', locals())

                base_user = models.BaseInfo.objects.get(baseId=input_student_id)
                username = base_user.baseName

                new_user = models.User()
                new_user.student_id = input_student_id
                new_user.name = username
                new_user.password = hash_code(password1)
                new_user.email = email
                new_user.save()

                code = make_confirm_string(new_user)
                send_email(email, code)
                message = '请前往邮箱进行确认！'
                return render(request, 'accounts/confirm.html', locals())
                # message = '注册成功'
                # return redirect("/accounts/login/")
        else:
            return render(request, 'accounts/register.html', locals())
    register_form = forms.RegisterForm()
    return render(request, 'accounts/register.html', locals())


def user_confirm(request):
    if request.session.get('is_login', None):
        return redirect('/accounts/index/')
    code = request.GET.get('code', None)
    message = ''
    try:
        confirm = models.ConfirmString.objects.get(code=code)
    except:
        message = '无效的确认请求!'
        return render(request, 'accounts/confirm.html', locals())

    c_time = confirm.c_time
    now = datetime.datetime.now()
    if str(now) > str(c_time + datetime.timedelta(settings.CONFIRM_DAYS)):
        confirm.user.delete()
        message = '您的邮件已经过期！请重新注册!'
        return render(request, 'accounts/confirm.html', locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = '感谢确认，请使用账户登录！'
        return render(request, 'accounts/confirm.html', locals())


def logout(request):
    if not request.session.get('is_login', None):
        return redirect('/accounts/login/')

    request.session.flush()
    # del request.session['is_login']
    return redirect("/accounts/login/")


def profile(request):
    if not request.session.get('is_login', None):
        return redirect('/accounts/login/')
    try:  # 更新战队信息
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
    solved = []
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
    return render(request, 'accounts/profile/profile.html', locals())


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
    return render(request, 'accounts/profile/change_pwd.html', locals())


def fun(request):
    return render(request, 'accounts/fun.html')


def forget(request):
    if request.session.get('is_login', None):
        return redirect('/accounts/index/')
    if request.method == 'POST':
        email_form = forms.EmailForm(request.POST)
        message = "请检查填写的内容！"
        if email_form.is_valid():
            input_email = email_form.cleaned_data.get('email')
            if not models.User.objects.filter(email=input_email).exists():
                message = '未找到此邮箱对应的用户'
                return render(request, 'accounts/forget.html', locals())
            user = models.User.objects.get(email=input_email)
            code = make_confirm_string(user)
            send_email_reset(input_email, code)
            message = '请前往邮箱重置密码！'
            return render(request, 'accounts/confirm.html', locals())
    email_form = forms.EmailForm()
    return render(request, 'accounts/forget.html', locals())


def reset_pwd(request):
    if request.session.get('is_login', None):
        return redirect('/accounts/index/')
    code = request.GET.get('code', None)
    try:
        confirm = models.ConfirmString.objects.get(code=code)
    except:
        message = '无效的确认请求!'
        return render(request, 'accounts/confirm.html', locals())
    if request.method == 'POST':
        reset_form = forms.ResetForm(request.POST)
        user = confirm.user
        message = "请检查填写的内容！"
        if reset_form.is_valid():
            new_password = reset_form.cleaned_data.get('new_password')
            confirm_password = reset_form.cleaned_data.get('confirm_password')

            if len(str(new_password)) < 6:
                message = '密码长度不得小于6位啊亲'
                return render(request, 'accounts/reset.html', locals())
            elif new_password != confirm_password:
                message = '两次输入的密码不同！'
                return render(request, 'accounts/reset.html', locals())

            user.password = hash_code(new_password)
            user.save()
            confirm.delete()
            message = '修改成功！'
            return render(request, 'accounts/confirm.html', locals())

        else:
            return render(request, 'accounts/reset.html', locals())
    reset_form = forms.ResetForm()
    return render(request, 'accounts/reset.html', locals())

def suggest(request):
    if not request.session.get('is_login', None):
        return redirect('/accounts/login/')
    if request.method == 'POST':
        suggestion = models.Suggestion()
        suggestion.user_name = request.session['user_name']
        suggestion.suggestion = request.POST.get('message')
        suggestion.save()
        message = '感谢您的建议！'
        return render(request, 'accounts/index.html', locals())


