from django.shortcuts import render

from .models import FriendResult, Rule


def table_headers():
    return ["Name", "Score"]


def score_fs(r, fs):
    scores = {
        "PA": r.participate,
        "HI": r.hit,
        "BU": r.bullseye,
    }
    return {
        "name": f'{fs.prediction.friend.first_name} {fs.prediction.friend.last_name}',
        "score": scores[fs.result],
    }


def match(request, match_id):
    friend_results = FriendResult.objects.filter(prediction__match__id=match_id)
    rule = Rule.objects.get(id=friend_results[0].prediction.match.stage.id)
    ths = table_headers()
    scores = [score_fs(rule, friend_result) for friend_result in friend_results]
    context = {
        "rows": sorted(scores, key=lambda x: x["score"], reverse=True),
        "table_headers": ths,
        "title": friend_results[0].prediction.match,
    }
    return render(request, "tournaments/match_result.html", context)
