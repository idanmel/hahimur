from django.db.models import F, Sum, Value
from django.db.models.functions import Concat
from django.shortcuts import render

from .models import Match, Prediction, Tournament


def table_headers():
    return ["Name", "Prediction", "Score"]


def match_result_row(prediction):
    return {
        "name": f'{prediction.friend.first_name} {prediction.friend.last_name}',
        "prediction": f'{prediction.match.home_team} {prediction.home_score} - {prediction.away_score} {prediction.match.away_team}',
        "score": prediction.score,
    }


def match(request, match_id):
    m = Match.objects.get(id=match_id)
    predictions = Prediction.objects.filter(match=m).order_by("-score")
    ths = table_headers()
    rows = [match_result_row(friend_result) for friend_result in predictions]
    context = {
        "title": m,
        "table_headers": ["Name", "Prediction", "Score"],
        "rows": rows,
    }
    return render(request, "tournaments/match_result.html", context)


def matches(request, tournament_id):
    t = Tournament.objects.get(id=tournament_id)
    matches = Match.objects.filter(stage__tournament=t)
    context = {"matches": matches, "tournament": t}
    return render(request, "tournaments/matches.html", context)


def tournaments(request):
    ts = Tournament.objects.all()
    context = {"tournaments": ts}
    return render(request, "tournaments/index.html", context)


def sums(rs, fr):
    stage_id = fr.prediction.match.stage.id

    return {'name': f'{fr.prediction.friend.first_name} {fr.prediction.friend.last_name}'}


def standing(request, tournament_id):
    t = Tournament.objects.get(id=tournament_id)
    total_scores = Prediction.objects.values('friend__id').annotate(
        full_name=Concat(F('friend__first_name'), Value(' '), F('friend__last_name')),
        total=Sum('score')
    ).order_by("-total")
    context = {"rows": total_scores, "title": f"{t} - Standings", "headers": ["Name", "Scores"]}
    return render(request, "tournaments/standings.html", context)
