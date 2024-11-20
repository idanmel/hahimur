import datetime

from django.contrib.auth.models import User
from django.db import IntegrityError, models


class Tournament(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return f'{self.name}'

    def serialize(self):
        return {"tournament_id": self.pk, "name": self.name}


class Stage(models.Model):
    name = models.CharField(max_length=200)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.tournament} {self.name}'

    def serialize(self):
        return {"stage_id": self.pk, "name": self.name}

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="tournament_stage_uniq",
                fields=['tournament', 'name']
            )
        ]


class Team(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return f'{self.name}'


class Match(models.Model):
    start_time = models.DateTimeField()
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, null=True)
    number = models.PositiveSmallIntegerField()
    # home_team = models.ForeignKey(Team, on_delete=models.CASCADE)
    # away_team = models.ForeignKey(Team, on_delete=models.CASCADE)
    # home_score = models.PositiveSmallIntegerField()
    # away_score = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{self.stage}: {self.number}'

    def serialize(self):
        return {"start_time": self.start_time, "number": self.number}

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="match_stage_number_uniq",
                fields=['stage', 'number']
            )
        ]


class Prediction(models.Model):
    class Result(models.TextChoices):
        PARTICIPATE = "PA",
        HIT = "HI",
        BULLSEYE = "BU",
        WRONG = "WR",

    friend = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_team', default=None, null=True)
    home_score = models.PositiveSmallIntegerField()
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_team', default=None, null=True)
    away_score = models.PositiveSmallIntegerField()
    result = models.CharField(
        max_length=2,
        choices=Result,
        default=Result.PARTICIPATE
    )
    goals = models.PositiveSmallIntegerField(default=0)
    assists = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        home_team = self.home_team or self.match.home_team
        away_team = self.away_team or self.match.away_team
        return (f'{self.friend.first_name.capitalize()} {self.friend.last_name.capitalize()} '
                f'|| {self.match.stage} '
                f'|| {home_team} {self.home_score} - {away_team} {self.away_score}')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="friend_match_uniq",
                fields=['friend', 'match']
            )
        ]
        ordering = ['-match__start_time']


class Rule(models.Model):
    stage = models.OneToOneField(Stage, on_delete=models.CASCADE)
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


class StagePrediction(models.Model):
    friend = models.ForeignKey(User, on_delete=models.CASCADE)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    position = models.PositiveSmallIntegerField()

    def __str__(self):
        return (f'{self.friend.first_name.capitalize()} {self.friend.last_name.capitalize()} '
                f'|| {self.stage} '
                f'|| {self.team} '
                f'|| {self.position}')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="stageprediction_friend_stage_team_uniq",
                fields=['friend', 'stage', 'team']
            ),
            models.UniqueConstraint(
                name="stageprediction_friend_stage_position_uniq",
                fields=['friend', 'stage', 'position']
            )
        ]
        ordering = ['friend', 'stage__tournament', 'stage', 'position']


class Score(models.Model):
    date = models.DateField(default=datetime.date.today)
    friend = models.ForeignKey(User, on_delete=models.CASCADE)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    prediction = models.ForeignKey(Match, on_delete=models.CASCADE, null=True)
    score = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return (f'{self.friend.first_name.capitalize()} {self.friend.last_name.capitalize()} '
                f'|| {self.match.stage} '
                f'|| {self.match} '
                f'|| score: {self.score}')

    class Meta:
        ordering = ['-date', 'friend']


def create_tournaments(tournaments_data):
    for tid, name in tournaments_data:
        create_tournament(tid, name)


def create_tournament(tid, name):
    try:
        return Tournament.objects.create(id=tid, name=name)
    except IntegrityError:
        pass


