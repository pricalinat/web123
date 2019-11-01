from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic import View
from .forms import flagForm
from django.http import HttpResponse
from . import models
from accounts import models as accounts_models


# Create your views here.


def index(request):
    if not request.session.get('is_login', None):
        return redirect('/accounts/login/')
    # challenge = models.Challenges.objects.all()
    challenge = models.Challenges.objects.order_by("point")
    data_re = []
    data_pwn = []
    data_web = []
    for c in challenge:
        if c.category == 0:     # re
            re = PassInsideView(c.name, c.category, c.message, c.point, c.file, c.flag, c.id)
            data_re.append(re)
        elif c.category == 2:   # pwn
            p = PassInsideView(c.name, c.category, c.message, c.point, c.file, c.flag, c.id)
            data_pwn.append(p)
        elif c.category == 1:   # web
            w = PassInsideView(c.name, c.category, c.message, c.point, c.file, c.flag, c.id)
            data_web.append(w)
    return render(request, 'challenges_list.html', locals())


class PassInsideView():
    name = ''
    category = ''
    message = ''
    point = ''
    file = ''
    flag = ''
    id = ''

    def __init__(self, name, category, message, point, file, flag, id):
        self.name = name
        self.category = category
        self.message = message
        self.point = point
        self.file = file
        self.flag = flag
        self.id = id


def solve(request, challenge_id):
    if not request.session.get('is_login', None):
        return redirect('/accounts/login/')
    challenge = models.Challenges.objects.get(id=challenge_id)
    user_id = accounts_models.User.id
    return render(request, 'solve.html', locals())


class IndexView(View):
    # def get(self, request, challenge_id):
    #     if not request.session.get('is_login', None):
    #         return redirect('/accounts/login/')
    #     form = flagForm()
    #     challenge = models.Challenges.objects.get(id=challenge_id)
    #
    #     return render(request, 'solve.html', {'challenge': challenge, 'form': form})

    def post(self, request, challenge_id):
        if not request.session.get('is_login', None):
            return redirect('/accounts/login/')
        # print(request.POST)
        flag = request.POST.get(str(challenge_id)+'_flag')
        # print(flag)
        challenge = models.Challenges.objects.get(id=challenge_id)
        current_id = request.session['user_id']
        current_user = accounts_models.User.objects.get(id=current_id)
        if challenge.solver.filter(id=current_id).exists():
            response = '<div id="flag_already"><p>ALREADY SUBMITTED</p></div>'
            return HttpResponse(response)
        else:
            if flag == challenge.flag:
                solver = current_user
                challenge.solver.add(solver)
                current_user.point += challenge.point
                current_user.save()
                try:
                    team = current_user.team
                    team.point += challenge.point
                    team.save()
                except:
                    pass
                response = '<div id="flag_correct"><p>CORRECT</p></div>'
                return HttpResponse(response)
            else:
                response = '<div id="flag_incorrect"><p>INCORRECT</p></div>'
                return HttpResponse(response)


        # form = flagForm(request.POST)
        # if form.is_valid():
        #     flag = form.cleaned_data.get('flag')
        #     challenge = models.Challenges.objects.get(id=challenge_id)
        #     current_id = request.session['user_id']
        #     current_user = accounts_models.User.objects.get(id=current_id)
        #     # challenge.solver.all()
        #
        #     if challenge.solver.filter(id=current_id).exists():
        #         response = '<div id="flag_already"><p>ALREADY SUBMITTED</p></div>'
        #         return HttpResponse(response)
        #     else:
        #         if flag == challenge.flag:
        #             solver = current_user
        #             challenge.solver.add(solver)
        #             current_user.point += challenge.point
        #             current_user.save()
        #             try:
        #                 team = current_user.team
        #                 team.point += challenge.point
        #                 team.save()
        #             except:
        #                 pass
        #             response = '<div id="flag_correct"><p>CORRECT</p></div>'
        #             return HttpResponse(response)
        #         else:
        #             response = '<div id="flag_incorrect"><p>INCORRECT</p></div>'
        #             return HttpResponse(response)
        # else:
        #     return HttpResponse('fail')
