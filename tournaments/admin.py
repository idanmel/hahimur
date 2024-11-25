from django.contrib import admin

from .models import Match, Prediction, Rule, Score, Stage, StagePoint, StagePrediction, Team, TopScorerPoint, \
    Tournament

admin.site.register(Tournament)
admin.site.register(Team)
admin.site.register(Match)
admin.site.register(Prediction)
admin.site.register(Stage)
admin.site.register(Rule)
admin.site.register(StagePrediction)
admin.site.register(Score)
admin.site.register(StagePoint)
admin.site.register(TopScorerPoint)
