from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.index),
    path('<int:challenge_id>/',views.IndexView.as_view()),
    path('collect/<int:challenge_id>/',views.collect),
    path('collection/',views.collection),
    path('sortedByDif/',views.sortedByDif),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
