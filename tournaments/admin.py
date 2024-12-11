from django.contrib import admin

from .models import GroupPrediction, Match, MatchPointRule, PredictionResult, RegisteredTournament, Stage, StagePoint, \
    Team, TopScorerPoint, Tournament

admin.site.register(Tournament)
admin.site.register(Stage)
admin.site.register(Team)
admin.site.register(Match)
admin.site.register(GroupPrediction)
admin.site.register(StagePoint)
admin.site.register(TopScorerPoint)
admin.site.register(PredictionResult)
admin.site.register(MatchPointRule)
admin.site.register(RegisteredTournament)
