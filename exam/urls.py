from django.urls import path
from . import views
from django.urls import include

urlpatterns = [
    path('set_exam/',views.set_exam),
    path('examination/',views.examination),
    path('end_exam/',views.end_exam, name="end_exam"),
]