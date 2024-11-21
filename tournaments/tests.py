import datetime

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase, TransactionTestCase
from django.utils.timezone import make_aware

from tournaments.models import Match, Prediction, Stage, Team, Tournament, create_tournament, create_tournaments
from tournaments.views import match_predictions_context, matches_context


def get_matches(t):
    return Match.objects.filter(stage__tournament=t)


def create_matches(numbers):
    t = create_tournament(tid=1, name="ASD")
    stage = Stage.objects.create(name="123", tournament=t)
    for number in numbers:
        Match.objects.create(
            start_time=make_aware(datetime.datetime.now()),
            stage=stage,
            number=number
        )
    return t


def get_tournaments():
    ts = Tournament.objects.all()
    serialized = [t.serialize() for t in ts]
    return {"tournaments": serialized}


class TournamentsTest(TransactionTestCase):
    def test_no_tournaments(self):
        create_tournaments([])
        context = get_tournaments()
        self.assertEqual(context, {"tournaments": []})

    def test_one_tournament(self):
        create_tournaments([(1, "Euro 2024")])
        context = get_tournaments()
        self.assertEqual(context, {"tournaments": [{"tournament_id": 1, "name": "Euro 2024"}]})

    def test_multiple_tournament(self):
        create_tournaments([(1, "Euro 2024"), (2, "Euro 2025"), (3, "World Cup 3012")])
        context = get_tournaments()
        self.assertEqual(context, {
            "tournaments": [
                {"tournament_id": 1, "name": "Euro 2024"},
                {"tournament_id": 2, "name": "Euro 2025"},
                {"tournament_id": 3, "name": "World Cup 3012"},
            ]
        })

    def test_same_tournament_name_twice(self):
        create_tournaments([(1, "Euro 2024"), (2, "Euro 2024")])
        context = get_tournaments()
        self.assertEqual(context, {"tournaments": [{"tournament_id": 1, "name": "Euro 2024"}]})


def stages_context(t):
    stages = Stage.objects.filter(tournament=t)
    return {"Tournament": t.serialize(), "stages": [s.serialize() for s in stages]}


def create_stage(t, s):
    try:
        return Stage.objects.create(id=s["stage_id"], tournament=t, name=s["name"])
    except IntegrityError:
        pass


class StagesTest(TransactionTestCase):
    def setUp(self):
        self.tournament = create_tournament(1, "Euro 2024")

    @staticmethod
    def create_test_stages(t, stages):
        for stage in stages:
            create_stage(t, stage)

    def get_test_stages(self, stages):
        self.create_test_stages(self.tournament, stages)
        return stages_context(self.tournament)

    def test_no_stages(self):
        stages = []
        context = self.get_test_stages(stages)
        self.assertEqual(context, {"Tournament": self.tournament.serialize(), "stages": stages})

    def test_one_stage(self):
        stages = [
            {"stage_id": 1, "name": "Group A"}
        ]
        context = self.get_test_stages(stages)
        self.assertEqual(context, {"Tournament": self.tournament.serialize(), "stages": stages})

    def test_multiple_stages(self):
        stages = [
            {"stage_id": 1, "name": "Group A"},
            {"stage_id": 2, "name": "Group B"},
            {"stage_id": 3, "name": "Round of 16"}
        ]
        context = self.get_test_stages(stages)
        self.assertEqual(context, {
            "Tournament": self.tournament.serialize(),
            "stages": stages
        })

    def test_unique_stages(self):
        stages = [
            {"stage_id": 1, "name": "Group A"},
            {"stage_id": 2, "name": "Group A"},
        ]
        context = self.get_test_stages(stages)
        self.assertEqual(context, {
            "Tournament": self.tournament.serialize(),
            "stages": [{"stage_id": 1, "name": "Group A"}]
        })


class MatchesTest(TransactionTestCase):
    def setUp(self):
        self.tournament = Tournament.objects.create(name="Euro 2024")
        self.stage = Stage.objects.create(tournament=self.tournament, name="Group A")

    def create_match(self, number, home_team=None, away_team=None, home_score=None, away_score=None):
        try:
            return Match.objects.create(start_time=datetime.datetime(2024, 11, 20, tzinfo=datetime.UTC),
                                        stage=self.stage, number=number, home_team=home_team, away_team=away_team,
                                        home_score=home_score, away_score=away_score)
        except IntegrityError:
            pass

    def create_matches(self, numbers):
        return [self.create_match(number) for number in numbers]

    def test_no_matches(self):
        self.create_matches([])
        context = matches_context(self.tournament, [])
        self.assertEqual(context, {
            "tournament": self.tournament.serialize(),
            "matches": [],
        })

    def test_one_match(self):
        matches = self.create_matches([1])
        context = matches_context(self.tournament, matches)
        self.assertEqual(context, {
            "tournament": self.tournament.serialize(),
            "matches": [match.serialize() for match in matches if match],
        })

    def test_multiple_matches(self):
        matches = self.create_matches(range(5))
        context = matches_context(self.tournament, matches)
        self.assertEqual(context, {
            "tournament": self.tournament.serialize(),
            "matches": [match.serialize() for match in matches if match],
        })

    def test_matches_with_same_stage_and_number(self):
        matches = self.create_matches([1, 1])
        context = matches_context(self.tournament, matches)
        self.assertEqual(context, {
            "tournament": self.tournament.serialize(),
            "matches": [match.serialize() for match in matches if match],
        })

    def test_match_without_teams(self):
        match = self.create_match(1)
        self.assertEqual(match.serialize()["str"], "Unknown - Unknown")

    def test_match_with_only_one_team(self):
        match = self.create_match(number=1, home_team=Team.objects.create(name="Team A"))
        self.assertEqual(match.serialize()["str"], "Team A - Unknown")

    def test_match_not_finished(self):
        match = self.create_match(1, Team.objects.create(name="Team A"), Team.objects.create(name="Team B"))
        self.assertEqual(match.serialize()["str"], "Team A - Team B")

    def test_match_finished(self):
        match = self.create_match(
            1,
            home_team=Team.objects.create(name="Team A"),
            away_team=Team.objects.create(name="Team B"),
            home_score=0,
            away_score=0,
        )
        self.assertEqual(match.serialize()["str"], "Team A 0 - 0 Team B")


def create_prediction(match, name):
    try:
        friend = User.objects.create_user(username=name, first_name="Alon", last_name="Oak")
        return Prediction.objects.create(friend=friend, match=match, home_score=0, away_score=0)
    except Exception as e:
        print(e)


def create_predictions(match, names):
    return [create_prediction(match, name) for name in names]


class MatchPredictionsTest(TestCase):
    def setUp(self):
        self.tournament = Tournament.objects.create(name="Euro 2024")
        self.stage = Stage.objects.create(tournament=self.tournament, name="Group A")
        self.match = Match.objects.create(start_time=datetime.datetime(2024, 11, 20, tzinfo=datetime.UTC),
                                          stage=self.stage, number=1)
        self.friend = User.objects.create(username="Idan", first_name="Idan", last_name="Melamed")

    def test_no_predictions(self):
        context = match_predictions_context(self.tournament, self.match, [])
        self.assertEqual(context, {"tournament": self.tournament.serialize(), "match": self.match.serialize(),
                                   "predictions": []})

    def test_one_prediction(self):
        ps = create_predictions(self.match, ["idanmel"])
        context = match_predictions_context(self.tournament, self.match, ps)
        self.assertEqual(context, {"tournament": self.tournament.serialize(), "match": self.match.serialize(),
                                   "predictions": [p.serialize() for p in ps if p]})

    def test_multiple_predictions(self):
        ps = create_predictions(self.match, ["idanmel", "lichtertal", "eyalerez"])
        context = match_predictions_context(self.tournament, self.match, ps)
        self.assertEqual(context, {"tournament": self.tournament.serialize(), "match": self.match.serialize(),
                                   "predictions": [p.serialize() for p in ps if p]})
