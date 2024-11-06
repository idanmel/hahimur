from datetime import date

from django.shortcuts import render
from .models import FriendScore, get_matches


def index(request):
    matches = get_matches(1, 2024, 6, 14)
    queryset = FriendScore.objects.filter(prediction__match__start_time__date=date(2024, 6, 14))
    context = {"scores": queryset, "matches": matches}
    return render(request, "tournaments/index.html", context)
