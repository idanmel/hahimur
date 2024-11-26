from django.contrib import admin

from .models import Match, MatchPoint, Prediction, Stage, StagePoint, Team, TopScorerPoint, \
    Tournament

admin.site.register(Tournament)
admin.site.register(Stage)
admin.site.register(Team)
admin.site.register(Match)
admin.site.register(Prediction)
admin.site.register(StagePoint)
admin.site.register(TopScorerPoint)
admin.site.register(MatchPoint)
