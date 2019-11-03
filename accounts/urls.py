from django.urls import path
from . import views
from django.urls import include

urlpatterns = [
    path('', views.index),
    path('index/', views.index),
    path('login/', views.login),
    path('register/', views.register),
    path('logout/', views.logout),
    path('profile/',views.profile),
    path('profile/change_pwd/',views.change_pwd),
    path('fun/',views.fun),
    path('confirm/', views.user_confirm),
    path('captcha/', include('captcha.urls')),
    path('forget/',views.forget),
    path('reset/',views.reset_pwd),
]