import datetime

from django.contrib.auth.models import User
from django.db import models


class Tournament(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.name}'


class Stage(models.Model):
    name = models.CharField(max_length=200)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.tournament} {self.name}'


class Team(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.name}'


class Match(models.Model):
    start_time = models.DateTimeField()
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, null=True)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away')

    def __str__(self):
        return f'{self.stage}: {self.home_team} - {self.away_team}'


class Prediction(models.Model):
    friend = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_team', default=None, null=True)
    home_score = models.IntegerField()
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_team', default=None, null=True)
    away_score = models.IntegerField()

    def __str__(self):
        home_team = self.home_team or self.match.home_team
        away_team = self.away_team or self.match.away_team
        return (f'{self.friend.first_name.capitalize()} {self.friend.last_name.capitalize()} '
                f'[{self.match.stage}]: '
                f'{home_team} {self.home_score} - {away_team} {self.away_score}')


class FriendResult(models.Model):
    class Result(models.TextChoices):
        PARTICIPATE = "PA",
        HIT = "HI",
        BULLSEYE = "BU",

    prediction = models.ForeignKey(Prediction, on_delete=models.CASCADE)
    result = models.CharField(
        max_length=2,
        choices=Result,
        default=Result.PARTICIPATE
    )
    goals = models.PositiveSmallIntegerField(default=0)
    assists = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return (f'{self.prediction.friend.first_name.capitalize()} {self.prediction.friend.last_name.capitalize()} '
                f'[{self.prediction.match}] {self.Result(self.result).label}, Goals: {self.goals}, Assists: '
                f'{self.assists}')


class Rule(models.Model):
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    participate = models.PositiveSmallIntegerField(default=0)
    hit = models.PositiveSmallIntegerField(default=0)
    bullseye = models.PositiveSmallIntegerField(default=0)
    goals = models.PositiveSmallIntegerField(default=0)
    assists = models.PositiveSmallIntegerField(default=0)
    advance = models.PositiveSmallIntegerField(default=0)
    advanced_position = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f'{self.stage}'


def get_matches(id, year, month, day):
    return Match.objects.filter(
        stage__tournament_id=id,
        start_time__date=datetime.date(year, month, day)
    )
