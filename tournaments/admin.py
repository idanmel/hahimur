from django.contrib import admin

from .models import FriendResult, Match, Prediction, Rule, Stage, Team, Tournament

admin.site.register(Tournament)
admin.site.register(Team)
admin.site.register(Match)
admin.site.register(Prediction)
admin.site.register(Stage)
admin.site.register(FriendResult)
admin.site.register(Rule)


class PredictionAdmin(admin.ModelAdmin):
    model = Prediction
    list_display = ['title', 'get_author_name']

    @admin.display(description='Author Name', ordering='author__name')
    def get_author_name(self, obj):
        return obj.author.name