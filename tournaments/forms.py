from django.forms import ModelForm

from tournaments.models import Prediction


class PredictionForm(ModelForm):
    class Meta:
        model = Prediction
        fields = ['match', 'home_score', 'away_score', 'result']
