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
    challenge = models.Challenges.objects.all()
    return render(request, 'challenges_list.html', locals())

def solve(request, challenge_id):
    if not request.session.get('is_login', None):
        return redirect('/accounts/login/')
    challenge = models.Challenges.objects.get(id=challenge_id)
    user_id = accounts_models.User.id
    return render(request, 'solve.html', locals())


class IndexView(View):
    def get(self, request, challenge_id):
        if not request.session.get('is_login', None):
            return redirect('/accounts/login/')
        form = flagForm()
        challenge = models.Challenges.objects.get(id=challenge_id)

        return render(request, 'solve.html', {'challenge': challenge, 'form': form})

    def post(self, request, challenge_id):
        if not request.session.get('is_login', None):
            return redirect('/accounts/login/')
        form = flagForm(request.POST)
        if form.is_valid():
            flag = form.cleaned_data.get('flag')
            challenge = models.Challenges.objects.get(id=challenge_id)
            current_id = request.session['user_id']
            current_user = accounts_models.User.objects.get(id=current_id)
            # challenge.solver.all()

            if challenge.solver.filter(id=current_id).exists():
                return HttpResponse('have done')
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
                    return HttpResponse('success')
                else:
                    return HttpResponse('wrong')
        else:
            return HttpResponse('fail')
