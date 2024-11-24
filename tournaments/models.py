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


def with_default(v, d):
    if v is None:
        return d
    return v


class Match(models.Model):
    start_time = models.DateTimeField()
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, null=True)
    number = models.PositiveSmallIntegerField()
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="home", default=None, null=True)
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="away", default=None, null=True)
    home_score = models.PositiveSmallIntegerField(default=None, null=True)
    away_score = models.PositiveSmallIntegerField(default=None, null=True)

    def __str__(self):
        return f'{self.stage} || {self.number} || {self.user_friendly()}'

    @staticmethod
    def team_str(team):
        return with_default(team, "Unknown")

    @staticmethod
    def score_str(score):
        return with_default(score, "")

    def user_friendly(self):
        blah = [
            f"{self.team_str(self.home_team)}",
            f"{self.score_str(self.home_score)}",
            "-",
            f"{self.score_str(self.away_score)}",
            f"{self.team_str(self.away_team)}"
        ]
        blah2 = [b for b in blah if b]
        return " ".join(blah2)

    def serialize(self):
        return {
            "match_id": self.pk,
            "start_time": self.start_time,
            "number": self.number,
            "home_team": self.home_team,
            "home_score": self.home_score,
            "away_team": self.away_team,
            "away_score": self.away_score,
            "stage": self.stage.serialize(),
            "str": self.user_friendly()
        }

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="match_stage_number_uniq",
                fields=['stage', 'number']
            )
        ]
        verbose_name_plural = "Matches"
        ordering = ['-start_time', 'stage', '-number']


class Prediction(models.Model):
    class Result(models.TextChoices):
        WRONG = "WO",
        HIT = "HI",
        BULLSEYE = "BU",
        NOT_PARTICIPATED = "NO",

    friend = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_team', default=None, null=True)
    home_score = models.PositiveSmallIntegerField()
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_team', default=None, null=True)
    away_score = models.PositiveSmallIntegerField()
    result = models.CharField(
        max_length=2,
        choices=Result,
        default=None,
        null=True
    )
    goals = models.PositiveSmallIntegerField(default=0)
    assists = models.PositiveSmallIntegerField(default=0)
    points = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        home_team = self.home_team or self.match.home_team
        away_team = self.away_team or self.match.away_team
        return (f'{self.friend.first_name.capitalize()} {self.friend.last_name.capitalize()} '
                f'|| {self.match.stage} '
                f'|| {home_team} {self.home_score} - {self.away_score} {away_team} ')

    def user_friendly(self):
        return f"{self.home_team} {self.home_score} - {self.away_score} {self.away_team}"

    def serialize(self):
        return {
            "friend": serialize_friend(self.friend),
            "home_team": self.home_team,
            "home_score": self.home_score,
            "away_team": self.away_team,
            "away_score": self.away_score,
            "result": self.result,
            "points": self.points,
            "str": self.user_friendly(),
            "match": self.match.serialize(),
        }

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="friend_match_uniq",
                fields=['friend', 'match']
            )
        ]
        ordering = ['-points']


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

def serialize_friend(friend):
    return {"name": f"{friend.first_name} {friend.last_name}", "friend_id": friend.pk}

def friend_str(friend):
    return f"{friend.first_name.capitalize()} {friend.last_name.capitalize()}"


class StagePoint(models.Model):
    friend = models.ForeignKey(User, on_delete=models.CASCADE)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    points = models.PositiveSmallIntegerField(default=0)

    def serialize(self):
        return {
            "friend": serialize_friend(self.friend),
            "stage": self.stage.serialize(),
            "points": self.points,
        }

    def __str__(self):
        return f"{self.stage} || {friend_str(self.friend)} || {self.points}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="stagepoint_friend_stage",
                fields=['friend', 'stage']
            )
        ]
        ordering = ['stage', '-points', '-friend']

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


