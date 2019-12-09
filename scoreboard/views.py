from django.shortcuts import render, redirect
from accounts import models as a_models
from teams import models as t_models
from challenges import models as c_models


# Create your views here.
def index(request):
    if not request.session.get('is_login', None):
        return redirect('/accounts/login/')
    users = a_models.User.objects.all()
    teams = t_models.Team.objects.all()
    return render(request,'scoreboard/index.html',locals())