"""
The Tofes!

A friend should be able to fill a tofes, and then all his predictions should be saved

- When a friend saves a Group Match, his prediction should have the same teams as the Group match
with the score he predicted.
- When a friend saves the same Group Match again, it should update the prediction with the new score.
- In all the tofes, a player should not be able to pick the teams.
  - If it's a group match, the teams are the same as the group match
  - If it's a knockout match, the teams are calculated from the group matches.
- A friend should have a full tofes by the end
- A friend should be able to pick top goalscorer
- After a user saves all of Group A match predictions , a table should show the advancing teams
- After a user saves all Group match predictions, the knockout stage match should be populated
- After a user finishes with a KO match, the winner should be shown in the next KO match
- A user should be able to pick which team advances if a KO match ends in a tie

# Given a friend, see a match with open scores, and be able to save the scores for your prediction
# A friend who saves the scores to the same prediction, updates the score.

Friend A saves a prediction to a KO match which saves it with the same teams as a score of his choosing.
"""
from datetime import UTC, datetime

from django.contrib.auth.models import User
from django.test import TestCase

from tournaments.models import Match, MatchPointRule, GroupPrediction, PredictionResult, Stage, Team, Tournament


class PredictionResultTest(TestCase):
    def setUp(self):
        self.tournament = Tournament.objects.create(name="Euro 2024")
        self.stage = Stage.objects.create(name="Group A", tournament=self.tournament)
        self.home_team = Team.objects.create(name="Team A")
        self.away_team = Team.objects.create(name="Team B")
        self.match = Match.objects.create(
            start_time=datetime.now(UTC),
            stage=self.stage,
            home_team=self.home_team,
            away_team=self.away_team,
            number=1
        )
        self.friend = User.objects.create_user(username="idanmel")
        self.friend2 = User.objects.create_user(username="idanmel2")
        self.prediction = GroupPrediction.objects.create(
            friend=self.friend,
            match=self.match,
            home_score=1,
            away_score=1
        )
        self.prediction2 = GroupPrediction.objects.create(
            friend=self.friend2,
            match=self.match,
            home_score=2,
            away_score=2
        )
        self.match_point_rule = MatchPointRule.objects.create(
            stage=self.stage,
            wrong=0,
            hit=3,
            bullseye=5
        )

    def test_create_predictions_results(self):
        self.match.home_score = self.match.away_score = 1
        self.match.save()
        pr = PredictionResult.objects.get(prediction=self.prediction)
        self.assertEqual(pr.points, 5)
        pr2 = PredictionResult.objects.get(prediction=self.prediction2)
        self.assertEqual(pr2.points, 3)

    def test_update_prediction_result(self):
        PredictionResult.objects.create(prediction=self.prediction, points=5, result=PredictionResult.Result.BULLSEYE)
        PredictionResult.objects.create(prediction=self.prediction2, points=3, result=PredictionResult.Result.HIT)
        self.match.home_score = self.match.away_score = 3
        self.match.save()
        prs = PredictionResult.objects.all()
        for pr in prs:
            self.assertTrue(pr.hit())

    def test_prediction_result_when_match_returns_to_not_finished(self):
        PredictionResult.objects.create(prediction=self.prediction, points=5, result=PredictionResult.Result.BULLSEYE)
        PredictionResult.objects.create(prediction=self.prediction2, points=3, result=PredictionResult.Result.HIT)
        self.match.home_score = self.match.away_score = None
        self.match.save()
        prs = PredictionResult.objects.all()
        for pr in prs:
            self.assertTrue(pr.not_participated())
