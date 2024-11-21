from collections import defaultdict

from django.db.models import F, Sum, Value
from django.db.models.functions import Coalesce, Concat
from django.shortcuts import render

from .models import Match, Prediction, Score, StagePrediction, Tournament


def table_headers():
    return ["Name", "Prediction", "Score"]


def match_result_row(prediction):
    return {
        "name": f'{prediction["friend__first_name"]} {prediction["friend__last_name"]}',
        "prediction": f'{prediction["home_team__name"]} {prediction["home_score"]} - {prediction["away_score"]} {prediction["away_team__name"]}',
        "score": f'{prediction["score"]}'
    }


def match(request, match_id):
    m = Match.objects.get(id=match_id)
    predictions = Prediction.objects.filter(match=m).order_by("-friend")
    predictions_with_scores = (
        Prediction.objects
        .select_related('match', 'friend')  # Optimize related field lookups
        .annotate(
            score=Coalesce(
                Score.objects.filter(
                    match=F('match'),
                    friend=F('friend')
                ).values('score')[:1],  # Get the score value from Score
                Value(0)  # Default to 0 if no corresponding score is found
            )
        )
        .values(
            'friend__first_name',
            'friend__last_name',
            'home_team__name',
            'home_score',
            'away_team__name',
            'away_score',
            'result',
            'score',
        )
    )
    rows = [match_result_row(friend_result) for friend_result in predictions_with_scores]
    context = {
        "title": m,
        "table_headers": ["Name", "Prediction", "Score"],
        "rows": rows,
    }
    return render(request, "tournaments/match_result.html", context)


def matches(request, tournament_id):
    t = Tournament.objects.get(id=tournament_id)
    matches = Match.objects.filter(stage__tournament=t)
    context = {"tournament": t, "matches": [m.serialize() for m in matches if m]}
    return render(request, "tournaments/matches.html", context)


def tournaments(request):
    ts = Tournament.objects.all()
    context = {"tournaments": [t.serialize() for t in ts if t]}
    return render(request, "tournaments/index.html", context)


def sums(rs, fr):
    stage_id = fr.prediction.match.stage.id

    return {'name': f'{fr.prediction.friend.first_name} {fr.prediction.friend.last_name}'}


def standing(request, tournament_id):
    t = Tournament.objects.get(id=tournament_id)
    total_match_scores = (
        Prediction.objects
        .annotate(full_name=Concat(F('friend__first_name'), Value(' '), F('friend__last_name')))
        .values('full_name')
        .annotate(total=Sum('score'))
        .order_by("-full_name")
    )

    total_stage_scores = (
        StagePrediction.objects
        .filter(stage__tournament_id=tournament_id)
        .annotate(full_name=Concat(F('friend__first_name'), Value(' '),
                                   F('friend__last_name')))
        .values('full_name')
        .annotate(total=Sum('score'))
        .order_by("-full_name")
    )

    # Combine the scores by full_name
    combined_scores = defaultdict(int)

    # Add scores from total_match_scores
    for entry in total_match_scores:
        combined_scores[entry['full_name']] += entry['total']

    # Add scores from total_stage_scores
    for entry in total_stage_scores:
        combined_scores[entry['full_name']] += entry['total']

    # Convert combined_scores dictionary to a sorted list of dictionaries for easy display
    combined_scores_list = sorted(
        [{'full_name': name, 'total': score} for name, score in combined_scores.items()],
        key=lambda x: x['total'],
        reverse=True
    )

    context = {"rows": combined_scores_list,
               "title": f"{t} - Standings",
               "headers": ["Name", "Scores"]}
    return render(request, "tournaments/standings.html", context)
