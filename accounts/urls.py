from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
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
    path('captcha/', include('captcha.urls')),
]