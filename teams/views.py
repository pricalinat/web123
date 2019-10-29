from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import generic
from . import forms
from . import models
from accounts.models import User


# Create your views here.
def index(request):
    if not request.session.get('is_login', None):
        return redirect('/accounts/login/')
    teams = models.Team.objects.all()
    return render(request, 'teams/team_list.html', {'teams': teams})


def create(request):
    if not request.session.get('is_login', None):
        return redirect('/accounts/login/')
    if request.method == 'POST':
        team_n = forms.TeamForm(request.POST)
        user = User.objects.get(id=request.session['user_id'])
        if team_n.is_valid():
            teamname = team_n.cleaned_data.get('teamname')  # 读取表单返回的值
            if len(str(teamname)) > 20:  # 队名长度限制 后面的话是不是多余的
                message = '队名长度不得大于20个字符或者为空'
                return render(request, 'teams/teamcreate.html', locals())
            # if user.team.team_name!=None:
            #     message = '您已经拥有所属战队'
            #     return render(request, 'teams/teamcreate.html', locals())
            try:
                temp = user.team.team_name
                message = '您已经拥有所属战队'  # 不报错就说明有战队了
                return render(request, 'teams/teamcreate.html', locals())
            except:
                same_team_name = models.Team.objects.filter(team_name=teamname)  # 搜索队名为teamname的团队
                if same_team_name:  # 队名不能重复
                    message = '该战队已经存在'
                    return render(request, 'teams/teamcreate.html', locals())
                else:
                    # user=models.User.objects.filter(name='teamcreater'):#队名合法进行创建
                    # if user:
                    new_team = models.Team()
                    new_team.team_name = teamname
                    new_team.team_leader = user.name
                    new_team.point = user.point
                    new_team.save()
                    user.team = new_team
                    user.save()
                    request.session['team_name'] = user.team.team_name
                    request.session['is_leader'] = 1
                    message = '创建成功'
                    return render(request, 'teams/teamcreate.html', locals())

    team_n = forms.TeamForm()  # 重置??
    return render(request, 'teams/teamcreate.html', locals())


def join(request,team_id):
    if not request.session.get('is_login', None):
        return redirect('/accounts/login/')
    user = User.objects.get(id=request.session['user_id'])
    teams = models.Team.objects.all()
    try:
        temp = user.team.team_name
        message = '您已经拥有所属战队'  # 不报错就说明有战队了
        return render(request, 'teams/team_list.html', locals())
    except:
        team = models.Team.objects.get(id=team_id)
        if team.team_number>=5:
            message = '该站队人数已达上限~'
            return render(request, 'teams/team_list.html', locals())
        user.team=team
        team.point += user.point
        user.save()
        team.team_number += 1
        team.save()
        request.session['team_name'] = user.team.team_name
        message = '您已成功加入此战队^……^'
        return render(request, 'teams/team_list.html', locals())

def detail(request, team_id):
    if not request.session.get('is_login', None):
        return redirect('/accounts/login/')
    team = models.Team.objects.get(id=team_id)
    team_detail={}
    team_detail['id'] = team.id
    team_detail['name'] = team.team_name
    team_detail['number'] = team.team_number
    # team_detail['leader'] = team.team_leader
    members=User.objects.filter(team=team)
    # leader = User.objects.get(name=team.team_leader)
    # members.remove(leader)    # 语法错误，列表才有remove
    team_detail['members'] = members
    team_detail['score'] = team.point    # 还没写好！
    return render(request, 'teams/detail.html', {'team_detail': team_detail})


def manage(request):
    if not request.session.get('is_login', None):
        return redirect('/accounts/login/')
    if request.session['is_leader'] == 0:
        return redirect('/accounts/profile/')
    else:
        user = User.objects.get(id=request.session['user_id'])
        team = user.team
        members = User.objects.filter(team=team)
        number = team.team_number
        if request.method == 'POST':
            updateName_form = forms.updateName(request.POST)
            message = '请检查填写的内容！'
            if updateName_form.is_valid():
                new_name = updateName_form.cleaned_data.get('teamname')
                team.team_name=new_name
                team.save()
                request.session['team_name'] = user.team.team_name
                message = '修改成功！'
                return render(request, 'teams/manage.html', locals())
            else:
                return render(request,'teams/manage.html',locals())
        updateName_form = forms.updateName()
        return render(request, 'teams/manage.html', locals())

def delete_member(request,user_id):
    if not request.session.get('is_login', None):
        return redirect('/accounts/login/')
    if request.session['is_leader'] == 0:
        return redirect('/accounts/profile/')
    else:
        d_user = User.objects.get(id=user_id)
        team = models.Team.objects.get(team_name=request.session['team_name'])
        d_user.team = None
        d_user.save()
        team.team_number-=1
        team.point -= d_user.point
        team.save()
        message = '成功将'+d_user.name+'移出战队'
        user = User.objects.get(id=request.session['user_id'])
        members = User.objects.filter(team=team)
        number = team.team_number
        updateName_form = forms.updateName()
        return render(request, 'teams/manage.html', locals())

def disband(request):
    if not request.session.get('is_login', None):
        return redirect('/accounts/login/')
    if request.session['is_leader'] == 0:
        return redirect('/accounts/profile/')
    else:
        team = models.Team.objects.get(team_name=request.session['team_name'])
        team.delete()
        request.session['is_leader'] = 0
        return redirect('/')