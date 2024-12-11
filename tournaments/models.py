from tokenize import group

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_delete, post_save
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

    def is_finished(self):
        return self.home_score is not None and self.away_score is not None

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
            ),
            models.UniqueConstraint(
                name="match_stage_home_team_away_team",
                fields=['stage', 'home_team', 'away_team']
            )
        ]
        verbose_name_plural = "Matches"
        ordering = ['-start_time', 'stage', '-number']


class GroupPrediction(models.Model):
    friend = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    home_score = models.PositiveSmallIntegerField(null=True)
    away_score = models.PositiveSmallIntegerField(null=True)

    def __str__(self):
        return (f'{self.friend.first_name.capitalize()} {self.friend.last_name.capitalize()} '
                f'|| {self.match.stage} '
                f'|| {self.match.home_team} {self.home_score} - {self.away_score} {self.match.away_team} ')

    def user_friendly(self):
        return f"{self.match.home_team} {self.home_score} - {self.away_score} {self.match.away_team}"

    def is_home_win(self):
        return self.home_score > self.away_score

    def is_away_win(self):
        return self.away_score > self.home_score

    def is_draw(self):
        return self.home_score == self.away_score

    def serialize(self):
        return {
            "stage": self.match.stage.serialize(),
            "friend": serialize_friend(self.friend),
            "home_score": self.home_score,
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

    def is_hit(self):
        return ((self.home_score - self.away_score > 0 and self.match.home_score - self.match.away_score > 0)
                or (self.home_score - self.away_score < 0 and self.match.home_score - self.match.away_score < 0)
                or (self.home_score - self.away_score == 0 and self.match.home_score - self.match.away_score == 0))


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


class PredictionResult(models.Model):
    class Result(models.TextChoices):
        WRONG = "WO",
        HIT = "HI",
        BULLSEYE = "BU",
        NOT_PARTICIPATED = "NO"

    prediction = models.OneToOneField(GroupPrediction, on_delete=models.CASCADE)
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

    def not_participated(self):
        return self.points == 0 and self.result == self.Result.NOT_PARTICIPATED

    def hit(self):
        return self.points == 3 and self.result == self.Result.HIT


def update_total_points(friend, tournament):
    top_scorer_points = TopScorerPoint.objects.filter(
        friend=friend,
        match__stage__tournament=tournament
    ).aggregate(total=Sum('points'))['total'] or 0

    prediction_points = PredictionResult.objects.filter(
        prediction__friend=friend,
        prediction__match__stage__tournament=tournament
    ).aggregate(total=Sum('points'))['total'] or 0

    stage_points = StagePoint.objects.filter(
        friend=friend,
        stage__tournament=tournament
    ).aggregate(total=Sum('points'))['total'] or 0

    total_points = top_scorer_points + prediction_points + stage_points
    TotalPoint.objects.update_or_create(
        friend=friend,
        tournament=tournament,
        defaults={'points': total_points}
    )


@receiver([post_save, post_delete], sender=PredictionResult)
def update_total_points_after_prediction_result(sender, instance, **kwargs):
    tournament = instance.prediction.match.stage.tournament
    friend = instance.prediction.friend
    update_total_points(friend, tournament)


@receiver([post_save, post_delete], sender=TopScorerPoint)
def update_total_points_after_top_scorer_point(sender, instance, **kwargs):
    tournament = instance.match.stage.tournament
    friend = instance.friend
    update_total_points(friend, tournament)


@receiver([post_save, post_delete], sender=StagePoint)
def update_total_points_after_stage_point(sender, instance, **kwargs):
    tournament = instance.stage.tournament
    friend = instance.friend
    update_total_points(friend, tournament)


def is_hit(prediction, match):
    return ((prediction.home_score - prediction.away_score > 0 and match.home_score - match.away_score > 0)
            or (prediction.home_score - prediction.away_score < 0 and match.home_score - match.away_score < 0)
            or (prediction.home_score - prediction.away_score == 0 and match.home_score - match.away_score == 0))


def same_scores(prediction, match):
    return prediction.home_score == match.home_score and prediction.away_score == match.away_score


def get_points_and_result(rule, prediction, match):
    points = rule.wrong
    result = PredictionResult.Result.WRONG

    if is_hit(prediction, match):
        points = rule.hit
        result = PredictionResult.Result.HIT

    if same_scores(prediction, match):
        points = rule.bullseye
        result = PredictionResult.Result.BULLSEYE

    return points, result


@receiver(post_save, sender=Match)
def update_prediction_results(sender, instance, **kwargs):
    match_point_rule = MatchPointRule.objects.filter(stage=instance.stage).first()
    if match_point_rule is None:
        return None
    gps = GroupPrediction.objects.filter(match=instance)
    for gp in gps:
        if not instance.is_finished():
            points, result = 0, PredictionResult.Result.NOT_PARTICIPATED
        else:
            points, result = get_points_and_result(match_point_rule, gp, instance)
        PredictionResult.objects.update_or_create(prediction=gp,
                                                  defaults={'points': points, 'result': result})


class MatchPointRule(models.Model):
    stage = models.OneToOneField(Stage, on_delete=models.CASCADE)
    wrong = models.PositiveSmallIntegerField()
    hit = models.PositiveSmallIntegerField()
    bullseye = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.stage} || {self.wrong} || {self.hit} || {self.bullseye}"


class RegisteredTournament(models.Model):
    friend = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="registered_tournament_tournament_friend",
                fields=['friend', 'tournament']
            )
        ]


@receiver(post_save, sender=RegisteredTournament)
def create_start_predictions(sender, instance, **kwargs):
    matches = Match.objects.filter(stage__tournament=instance.tournament)
    for match in matches:
        GroupPrediction.objects.get_or_create(
            friend=instance.friend,
            match=match,
            defaults={
                "home_score": None,
                "away_score": None,
            }
        )


@receiver(post_delete, sender=RegisteredTournament)
def create_start_predictions(sender, instance, **kwargs):
    GroupPrediction.objects.filter(match__stage__tournament=instance.tournament, friend=instance.friend).delete()


class GroupRow(models.Model):
    friend = models.ForeignKey(User, on_delete=models.CASCADE)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    pld = models.PositiveSmallIntegerField(default=0)
    wins = models.PositiveSmallIntegerField(default=0)
    draws = models.PositiveSmallIntegerField(default=0)
    losses = models.PositiveSmallIntegerField(default=0)
    gf = models.PositiveSmallIntegerField(default=0)
    ga = models.PositiveSmallIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="group_row_friend_stage_team",
                fields=['friend', 'stage', 'team']
            )
        ]

    def position(self):
        return 1

    def __str__(self):
        return f"{self.stage} || {self.team} || {self.position()}"

    def points(self):
        return self.wins * 3 + self.draws

    def goal_difference(self):
        return self.gf - self.ga

    def serialize(self):
        return {
            "friend": serialize_friend(self.friend),
            "tournament": self.stage.tournament.serialize(),
            "stage": self.stage.serialize(),
            "team": self.team.serialize(),
            "position": self.position,
            "points": self.points,
            "played": self.pld,
            "wins": self.wins,
            "draws": self.draws,
            "losses": self.losses,
            "goals_for": self.gf,
            "goals_against": self.ga,
            "goal_difference": self.goal_difference(),
        }

def default_group_row(friend, stage, team):
    return GroupRow(
        friend=friend,
        stage=stage,
        team=team,
        pld=0,
        wins=0,
        draws=0,
        losses=0,
        gf=0,
        ga=0
    )


@receiver(post_save, sender=GroupPrediction)
def create_start_predictions(sender, instance, **kwargs):
    group_predictions = GroupPrediction.objects.filter(match__stage=instance.match.stage, friend=instance.friend)
    GroupRow.objects.filter(friend=instance.friend, stage=instance.match.stage).delete()
    teams = set([group_prediction.match.home_team for group_prediction in group_predictions]) | set([group_prediction.match.away_team for group_prediction in group_predictions])
    group_table = {team.name: default_group_row(instance.friend, instance.match.stage, team) for team in teams}
    print(group_table)

    for group_prediction in group_predictions:
        team_name = group_prediction.match.home_team.name
        group_table[team_name].pld += 1
        group_table[team_name].wins += 1 if group_prediction.is_home_win() else 0
        group_table[team_name].draws += 1 if group_prediction.is_draw() else 0
        group_table[team_name].losses += 1 if group_prediction.is_away_win() else 0
        group_table[team_name].gf += group_prediction.home_score
        group_table[team_name].ga += group_prediction.away_score
        group_table[team_name].save()

        team_name = group_prediction.match.away_team.name
        group_table[team_name].pld += 1
        group_table[team_name].wins += 1 if group_prediction.is_away_win() else 0
        group_table[team_name].draws += 1 if group_prediction.is_draw() else 0
        group_table[team_name].losses += 1 if group_prediction.is_home_win() else 0
        group_table[team_name].gf += group_prediction.away_score
        group_table[team_name].ga += group_prediction.home_score
        group_table[team_name].save()



    print(group_predictions)
    return []
