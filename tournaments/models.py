from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver


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

    class Meta:
        ordering = ["-name"]

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
    home_score = models.PositiveSmallIntegerField(default=None, null=True)
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="away", default=None, null=True)
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
    friend = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_team', default=None, null=True)
    home_score = models.PositiveSmallIntegerField()
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_team', default=None, null=True)
    away_score = models.PositiveSmallIntegerField()

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
            "stage": self.match.stage.serialize(),
            "friend": serialize_friend(self.friend),
            "home_team": self.home_team,
            "home_score": self.home_score,
            "away_team": self.away_team,
            "away_score": self.away_score,
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


class TopScorerPoint(models.Model):
    friend = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    points = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return (f"{self.friend.first_name.capitalize()} {self.friend.last_name.capitalize()} "
                f"|| {self.match} "
                f"|| Points: {self.points}")

    def serialize(self):
        return {
            "friend": serialize_friend(self.friend),
            "match": self.match.serialize(),
            "points": self.points,
        }


class TotalPoint(models.Model):
    friend = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    points = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return (f"{self.friend.first_name.capitalize()} {self.friend.last_name.capitalize()} "
                f"|| {self.tournament} "
                f"|| Points: {self.points}")

    def serialize(self):
        return {
            "friend": serialize_friend(self.friend),
            "tournament": self.tournament.serialize(),
            "points": self.points,
        }

    class Meta:
        ordering = ['-points', '-friend']


@receiver(post_save, sender=TopScorerPoint)
@receiver(post_save, sender=Prediction)
@receiver(post_save, sender=StagePoint)
def update_total_points(sender, instance, **kwargs):
    friend = instance.friend

    # Determine the tournament based on the instance type
    if isinstance(instance, TopScorerPoint):
        tournament = instance.match.stage.tournament
    elif isinstance(instance, Prediction):
        tournament = instance.match.stage.tournament
    elif isinstance(instance, StagePoint):
        tournament = instance.stage.tournament
    else:
        return  # Invalid instance type

    # Calculate total points from TopScorerPoint
    top_scorer_points = TopScorerPoint.objects.filter(
        friend=friend,
        match__stage__tournament=tournament
    ).aggregate(total=Sum('points'))['total'] or 0

    # Calculate total points from Prediction
    prediction_points = PredictionResult.objects.filter(
        prediction__friend=friend,
        prediction__match__stage__tournament=tournament
    ).aggregate(total=Sum('points'))['total'] or 0

    # Calculate total points from StagePoint
    stage_points = StagePoint.objects.filter(
        friend=friend,
        stage__tournament=tournament
    ).aggregate(total=Sum('points'))['total'] or 0

    # Total all points
    total_points = top_scorer_points + prediction_points + stage_points

    # Update or create the TotalPoint entry
    TotalPoint.objects.update_or_create(
        friend=friend,
        tournament=tournament,
        defaults={'points': total_points}
    )


class PredictionResult(models.Model):
    class Result(models.TextChoices):
        WRONG = "WO",
        HIT = "HI",
        BULLSEYE = "BU",
        NOT_PARTICIPATED = "NO"

    prediction = models.OneToOneField(Prediction, on_delete=models.CASCADE)
    points = models.PositiveSmallIntegerField(default=0)
    result = models.CharField(
        max_length=2,
        choices=Result,
        default=None,
        null=True
    )

    def __str__(self):
        return f"{self.prediction} || points: {self.points} || {self.result}"

    def serialize(self):
        return {
            "stage": self.prediction.match.stage.serialize(),
            "match": self.prediction.match.serialize(),
            "friend": serialize_friend(self.prediction.friend),
            "str": self.prediction.user_friendly(),
            "points": self.points,
        }


def is_hit(prediction, match):
    return ((prediction.home_score - prediction.away_score > 0 and match.home_score - match.away_score > 0)
            or (prediction.home_score - prediction.away_score < 0 and match.home_score - match.away_score < 0)
            or (prediction.home_score - prediction.away_score == 0 and match.home_score - match.away_score == 0))


def same_scores(prediction, match):
    return prediction.home_score == match.home_score and prediction.away_score == match.away_score


def is_same_teams(prediction, match):
    return prediction.home_team == match.home_team and prediction.away_team == match.away_team


def get_points_and_result(rule, prediction, match):
    points = rule.wrong
    result = PredictionResult.Result.WRONG

    if not is_same_teams(prediction, match):
        points = rule.wrong
        result = PredictionResult.Result.NOT_PARTICIPATED

    if is_same_teams(prediction, match) and is_hit(prediction, match):
        points = rule.hit
        result = PredictionResult.Result.HIT

    if is_same_teams(prediction, match) and same_scores(prediction, match):
        points = rule.bullseye
        result = PredictionResult.Result.BULLSEYE

    return points, result


@receiver(post_save, sender=Prediction)
def update_prediction_results(sender, instance, **kwargs):
    match_point_rule = MatchPointRule.objects.get(stage=instance.match.stage)
    points, result = get_points_and_result(match_point_rule, instance, instance.match)
    PredictionResult.objects.update_or_create(prediction=instance,
                                              defaults={'points': points, 'result': result})


class MatchPointRule(models.Model):
    stage = models.OneToOneField(Stage, on_delete=models.CASCADE)
    wrong = models.PositiveSmallIntegerField()
    hit = models.PositiveSmallIntegerField()
    bullseye = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.stage} || {self.wrong} || {self.hit} || {self.bullseye}"
