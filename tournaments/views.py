from django.shortcuts import render

from .models import FriendResult, Rule


def table_headers():
    return ["Rank", "Name", "Score"]


def score_fs(r, fs):
    return {"name": f'{fs.prediction.friend.first_name} {fs.prediction.friend.last_name}', "score": 3}


def index(request):
    friend_results = FriendResult.objects.filter(prediction__match__id=1)
    rule = Rule.objects.get(id=1)
    ths = table_headers()
    scores = [score_fs(rule, friend_result) for friend_result in friend_results]
    context = {"rows": scores, "table_headers": ths}
    return render(request, "tournaments/index.html", context)
