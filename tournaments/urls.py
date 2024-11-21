from django.urls import path

from . import views

urlpatterns = [
    path("", views.tournaments, name="tournaments"),
    path("<int:tournament_id>/standings", views.standing, name="standings"),
    path("<int:tournament_id>/matches/<int:match_id>", views.match, name="match"),
    path("<int:tournament_id>/matches", views.matches, name="matches")
]