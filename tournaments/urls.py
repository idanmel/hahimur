from django.urls import path

from . import views

urlpatterns = [
    path("matches/<int:match_id>", views.match, name="match"),
]