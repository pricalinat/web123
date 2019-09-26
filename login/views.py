from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings
from . import models
from . import forms
import hashlib
import datetime
# Create your views here.


def hash_code(s, salt='mysite'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()


def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.name, now)
    models.ConfirmString.objects.create(code=code, user=user)
    return code


def index(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    return render(request, 'login/index.html')


def login(request):
    if request.session.get('is_login', None):  # 不允许重复登录
        return redirect('/index/')
    if request.method == 'POST':
        login_form = forms.UserForm(request.POST)
        message = '请检查填写的内容！'
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')

            try:
                user = models.User.objects.get(name=username)
            except :
                message = '用户不存在！'
                return render(request, 'login/login.html', locals())

            # if not user.has_confirmed:
            #     message = '该用户还未经过邮件确认！'
            #     return render(request, 'login/login.html', locals())

            if user.password == hash_code(password):
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                return redirect('/index/')
            else:
                message = '密码不正确！'
                print(user.password)
                return render(request, 'login/login.html', locals())
        else:
            return render(request, 'login/login.html', locals())

    login_form = forms.UserForm()
    return render(request, 'login/login.html', locals())


def register(request):
    if request.session.get('is_login', None):
        return redirect('/index/')

    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            # email = register_form.cleaned_data.get('email')
            sex = register_form.cleaned_data.get('sex')

            if len(str(password1))<6:   # 密码长度不能小于六位
                message = '密码长度不得小于6位啊亲'
                return render(request, 'login/register.html', locals())
            elif password1 != password2:
                message = '两次输入的密码不同！'
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:
                    message = '用户名已经存在'
                    return render(request, 'login/register.html', locals())
                # same_email_user = models.User.objects.filter(email=email)
                # if same_email_user:
                #     message = '该邮箱已经被注册了！'
                #     return render(request, 'login/register.html', locals())

                new_user = models.User()
                new_user.name = username
                new_user.password = hash_code(password1)
                # new_user.email = email
                new_user.sex = sex
                new_user.save()

                # code = make_confirm_string(new_user)
                # send_email(email, code) #把带e-mail的去掉，验证去掉（68）

                # message = '请前往邮箱进行确认！'
                # return render(request, 'login/confirm.html', locals())
                # message = '注册成功'
                return redirect("/login/")
        else:
            return render(request, 'login/register.html', locals())
    register_form = forms.RegisterForm()
    return render(request, 'login/register.html', locals())


def logout(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')

    request.session.flush()
    # del request.session['is_login']
    return redirect("/login/")


# def user_confirm(request):
#     code = request.GET.get('code', None)
#     message = ''
#
#     try:
#         confirm = models.ConfirmString.objects.get(code=code)
#     except:
#         message = '无效的确认请求！'
#         return render(request, 'login/confirm.html', locals())
#
#     c_time = confirm.c_time
#     now = datetime.datetime.now()
#     if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
#         confirm.user.delete()
#         message = '您的邮件已经过期！请重新注册！'
#         return render(request, 'login/confirm.html', locals())
#     else:
#         confirm.user.has_confirmed = True
#         confirm.user.save()
#         confirm.delete()
#         message = '感谢确认，请使用账户登录！'
#         return render(request, 'login/confirm.html', locals())




