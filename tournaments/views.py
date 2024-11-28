from django.contrib.auth.models import User
from django.forms import formset_factory
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from .forms import PredictionForm
from .models import Match, Prediction, PredictionResult, Stage, StagePoint, TopScorerPoint, TotalPoint, Tournament


def match(request, tournament_id, match_id):
    t = Tournament.objects.get(pk=tournament_id)
    m = Match.objects.get(pk=match_id)
    predictions_results = PredictionResult.objects.filter(prediction__match=m)
    context = match_predictions_context(t, m, predictions_results)
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


def match_prediction_stats(predictions_results):
    noes = [p for p in predictions_results if p.result == p.Result.NOT_PARTICIPATED]
    wrongs = [p for p in predictions_results if p.result == p.Result.WRONG]
    hits = [p for p in predictions_results if p.result == p.Result.HIT]
    bullseyes = [p for p in predictions_results if p.result == p.Result.BULLSEYE]
    points = [p.points for p in predictions_results]
    return {
        "wrongs": percentize(len(wrongs) / len(predictions_results)),
        "hit": percentize(len(hits) / len(predictions_results)),
        "bullseye": percentize(len(bullseyes) / len(predictions_results)),
        "played": percentize((len(predictions_results) - len(noes)) / len(predictions_results)),
        "points_avg": f"{sum(points) / len(points):.2f}".rstrip('0').rstrip('.'),
    }


def match_predictions_context(t, m, predictions_results):
    if not predictions_results:
        return {
            "tournament": t.serialize(),
            "match": m.serialize(),
        }
    return {
        "tournament": t.serialize(),
        "match": m.serialize(),
        "predictions": [p.serialize() for p in predictions_results if p],
        "statistics": match_prediction_stats(predictions_results),
    }


def stage_points_context(t, stage, stage_points, matches):
    return {
        "tournament": t.serialize(),
        "stage": stage.serialize(),
        "matches": [match.serialize() for match in matches if match],
        "stage_points": [stage_point.serialize() for stage_point in stage_points if stage_point]
    }


def stage_view(request, tournament_id, stage_id):
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
    ps = PredictionResult.objects.filter(prediction__match__stage__tournament=t, prediction__friend=f)
    stage_points = StagePoint.objects.filter(stage__tournament=t, friend=f)
    top_scorer_points = TopScorerPoint.objects.filter(match__stage__tournament=t, friend=f)
    total_points = TotalPoint.objects.get(tournament=t, friend=f)
    context = friend_results_context(t, f, ps, stage_points, top_scorer_points, total_points)
    return render(request, "tournaments/friend.html", context)


class FriendPredictions(View):
    def get(self, request, tournament_id, friend_id):
        t = Tournament.objects.get(pk=tournament_id)
        f = User.objects.get(pk=friend_id)
        matches = Match.objects.filter(stage__tournament=tournament_id)
        formset = formset_factory(PredictionForm, extra=len(matches))
        context = {
            "tournament": t.serialize(),
            "friend": {"name": f"{f.first_name} {f.last_name}", "friend_id": f.pk},
            "formset": formset,
        }
        return render(request, "tournaments/tofes_2024.html", context)

    def post(self, request, tournament_id, friend_id):
        PredictionFormSet = formset_factory(PredictionForm)
        formset = PredictionFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                print(form.cleaned_data["match"])
                Prediction.objects.update_or_create(
                    friend=User.objects.get(pk=friend_id),
                    match=form.cleaned_data["match"],
                    defaults={'home_score': form.cleaned_data["home_score"],
                              'away_score': form.cleaned_data["away_score"],
                              'home_team': form.cleaned_data["match"].home_team,
                              'away_team': form.cleaned_data["match"].away_team}
                )
        return HttpResponse(status=204)
