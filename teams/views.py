from django.shortcuts import render, redirect
from django.views import generic
from accounts.models import User
from . import forms
from . import models


# Create your views here.
def index(request):
    teams = models.Team.objects.all()
    return render(request, 'teams/team_list.html', {'teams': teams})


def teamcreate(request):  # 仿造注册流程写的  怎样将团队信息和个人信息联系在一起 创建完团队后将创建人的信息录入团队中
    if request.method == 'POST':
        team_n = forms.TeamForm(request.POST)
        # print('nop')
        if team_n.is_valid():  # is_valid校验    有个校验就过不去
            # print('yep')
            teamname = team_n.cleaned_data.get('teamname')  # 读取表单返回的值
            # teamcreater=team_n.cleaned_data.get('teamcreater')
            if len(str(teamname)) > 20:  # 队名长度限制 后面的话是不是多余的
                message = '队名长度不得大于20个字符或者为空'
                return render(request, 'teams/teamcreate.html', locals())
            else:
                same_team_name = models.Team.objects.filter(team_name=teamname)  # 搜索队名为teamname的团队
                if same_team_name:  # 队名不能重复
                    message = '该队名已经存在'
                    return render(request, 'teams/teamcreate.html', locals())
                else:
                    # user=models.User.objects.filter(name='teamcreater'):#队名合法进行创建
                    # if user:
                    new_team = models.Team()
                    new_team.team_name = teamname
                    new_team.save()  # !!!!!!还没有往accounts里存！！！！
                    message = '创建成功'
                    return render(request, 'teams/teamcreate.html', locals())

    team_n = forms.TeamForm()  # 重置??
    return render(request, 'teams/teamcreate.html', locals())

# def jointeam(request):
#  if request.method=='POST' :
#     pass
