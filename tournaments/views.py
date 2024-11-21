from collections import defaultdict

from django.db.models import F, Sum, Value
from django.db.models.functions import Concat
from django.shortcuts import render

from .models import Match, Prediction, Stage, StagePoint, StagePrediction, Tournament


def table_headers():
    return ["Name", "Prediction", "Score"]


def match_result_row(prediction):
    return {
        "name": f'{prediction["friend__first_name"]} {prediction["friend__last_name"]}',
        "prediction": f'{prediction["home_team__name"]} {prediction["home_score"]} - {prediction["away_score"]} {prediction["away_team__name"]}',
        "score": f'{prediction["score"]}'
    }


def match(request, tournament_id, match_id):
    t = Tournament.objects.get(pk=tournament_id)
    m = Match.objects.get(pk=match_id)
    predictions = Prediction.objects.filter(match=m)
    context = match_predictions_context(t, m, predictions)
    return render(request, "tournaments/match_predictions.html", context)


def matches(request, tournament_id):
    t = Tournament.objects.get(id=tournament_id)
    matches = Match.objects.filter(stage__tournament=t)
    return render(request, "tournaments/matches_page.html", matches_context(t, matches))


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


def matches_context(tournament, matches):
    return {
        "tournament": {"name": tournament.name, "tournament_id": tournament.pk},
        "matches": [m.serialize() for m in matches if m],
    }


def match_prediction_stats(predictions):
    if not predictions:
        return {}

    noes = [p for p in predictions if p.result == p.Result.NOT_PARTICIPATED]
    wrongs = [p for p in predictions if p.result == p.Result.WRONG]
    hits = [p for p in predictions if p.result == p.Result.HIT]
    bullseyes = [p for p in predictions if p.result == p.Result.BULLSEYE]
    points = [p.points for p in predictions]
    return {
        "wrongs": len(wrongs) / len(predictions) * 100,
        "hit": len(hits) / len(predictions) * 100,
        "bullseye": len(bullseyes) / len(predictions) * 100,
        "played": (len(predictions) - len(noes)) / len(predictions) * 100,
        "points_avg": sum(points) / len(points)
    }


def match_predictions_context(t, m, predictions):
    return {
        "tournament": t.serialize(),
        "match": m.serialize(),
        "predictions": [p.serialize() for p in predictions if p],
        "statistics": match_prediction_stats(predictions),
    }


def stage_points_context(t, stage, stage_points, matches):
    return {
        "tournament": t.serialize(),
        "stage": stage.serialize(),
        "matches": [match.serialize() for match in matches if match],
        "stage_points": [stage_point.serialize() for stage_point in stage_points if stage_point]
    }


def stage(request, tournament_id, stage_id):
    t = Tournament.objects.get(pk=tournament_id)
    s = Stage.objects.get(pk=stage_id)
    matches = Match.objects.filter(stage=s)
    stage_points = StagePoint.objects.filter(stage=s)
    context = stage_points_context(t, s, stage_points, matches)
    return render(request, "tournaments/stage.html", context)
