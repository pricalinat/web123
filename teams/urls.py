from django.urls import path
from . import views

urlpatterns=[
    path('',views.index),
    path('create/',views.create),
    path('detail/<int:team_id>/',views.detail),
    path('join/<int:team_id>/',views.join),
    path('manage/',views.manage),
    path('manage/delete/<int:user_id>/',views.delete_member),
    path('manage/disband/',views.disband),
]