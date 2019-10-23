from django.urls import path
from . import views

urlpatterns=[
    path('',views.index),
    path('create/',views.create),
    # path('join/',views.join),
    path('detail/<int:team_id>/',views.detail),
    path('join/<int:team_id>/',views.join),
]