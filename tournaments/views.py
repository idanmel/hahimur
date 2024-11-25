from django.contrib.auth.models import User
from django.shortcuts import render

from .models import Match, Prediction, Stage, StagePoint, TopScorerPoint, TotalPoint, Tournament


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


def standings_context(t, total_points):
    points = [tp.points for tp in total_points if tp]
    ranks = [points.index(value) + 1 for value in points]
    total_points = [tp.serialize() for tp in total_points if tp]

    for rank, total_point in zip(ranks, total_points):
        total_point["rank"] = rank

    return {
        "tournament": t.serialize(),
        "total_points": total_points
    }

def standing(request, tournament_id):
    t = Tournament.objects.get(id=tournament_id)
    total_points = TotalPoint.objects.filter(tournament=t)
    context = {"tournament": t.serialize()}
    if total_points:
        context = standings_context(t, total_points)
    return render(request, "tournaments/standings.html", context)


def matches_context(tournament, matches):
    return {
        "tournament": {"name": tournament.name, "tournament_id": tournament.pk},
        "matches": [m.serialize() for m in matches if m],
    }


def percentize(ratio):
    return f"{ratio * 100:.2f}".rstrip('0').rstrip('.') + "%"


def match_prediction_stats(predictions):
    noes = [p for p in predictions if p.result == p.Result.NOT_PARTICIPATED]
    wrongs = [p for p in predictions if p.result == p.Result.WRONG]
    hits = [p for p in predictions if p.result == p.Result.HIT]
    bullseyes = [p for p in predictions if p.result == p.Result.BULLSEYE]
    points = [p.points for p in predictions]
    return {
        "wrongs": percentize(len(wrongs) / len(predictions)),
        "hit": percentize(len(hits) / len(predictions)),
        "bullseye": percentize(len(bullseyes) / len(predictions)),
        "played": percentize((len(predictions) - len(noes)) / len(predictions)),
        "points_avg": f"{sum(points) / len(points):.2f}".rstrip('0').rstrip('.'),
    }


def match_predictions_context(t, m, predictions):
    if not predictions:
        return {
            "tournament": t.serialize(),
            "match": m.serialize(),
        }
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


def friend_results_context(t, f, ps, stage_points, top_scorer_points, total_points):
    predictions = [p.serialize() for p in ps if p]
    stage_points = [sp.serialize() for sp in stage_points if sp]
    top_scorer_points = [tsp.serialize() for tsp in top_scorer_points if tsp]
    return {
        "tournament": t.serialize(),
        "friend": f"{f.first_name} {f.last_name}",
        "predictions": predictions,
        "stage_points": stage_points,
        "top_scorer_points": top_scorer_points,
        "total_points": total_points.serialize(),
    }


def friend_results(request, tournament_id, friend_id):
    t = Tournament.objects.get(pk=tournament_id)
    f = User.objects.get(pk=friend_id)
    ps = Prediction.objects.filter(match__stage__tournament=t, friend=f)
    stage_points = StagePoint.objects.filter(stage__tournament=t, friend=f)
    top_scorer_points = TopScorerPoint.objects.filter(match__stage__tournament=t, friend=f)
    total_points = TotalPoint.objects.get(tournament=t, friend=f)
    context = friend_results_context(t, f, ps, stage_points, top_scorer_points, total_points)
    return render(request, "tournaments/friend.html", context)
