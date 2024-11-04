from django.contrib import admin

from .models import Match, Prediction, Stage, Team, Tournament

admin.site.register(Tournament)
admin.site.register(Team)
admin.site.register(Match)
admin.site.register(Prediction)
admin.site.register(Stage)
