from django.urls import path

from . import views

app_name = 'tournaments'

urlpatterns = [
    path("", views.tournaments, name="tournaments"),
    path("<int:tournament_id>/standings", views.standing, name="standings"),
    path("<int:tournament_id>/matches/<int:match_id>", views.match, name="match"),
    path("<int:tournament_id>/stages/<int:stage_id>", views.stage_view, name="stage"),
    path("<int:tournament_id>/matches", views.matches, name="matches"),
    path("<int:tournament_id>/friend/<int:friend_id>", views.friend_results, name="friend"),
    path("<int:tournament_id>/friend/<int:friend_id>/predictions/", views.FriendPredictions.as_view(), name="predictions"),
]
