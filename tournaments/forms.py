from django.forms import ModelForm

from tournaments.models import GroupPrediction


class PredictionForm(ModelForm):
    class Meta:
        model = GroupPrediction
        fields = ['match', 'home_score', 'away_score']
