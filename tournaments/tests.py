import datetime
from datetime import tzinfo

from django.db import IntegrityError
from django.test import TransactionTestCase
from django.utils.timezone import make_aware

from tournaments.models import Match, Stage, Tournament, create_tournament, create_tournaments


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


def matches_context(tournament, stage):
    return {
        "tournament": tournament.serialize(),
        "stage": stage.serialize(),
        "matches": [m.serialize() for m in Match.objects.filter(stage=stage)],
    }

class MatchesTest(TransactionTestCase):
    def setUp(self):
        self.tournament = Tournament.objects.create(name="Euro 2024")
        self.stage = Stage.objects.create(tournament=self.tournament, name="Group A")

    def create_match(self, number):
        try:
            return Match.objects.create(start_time=datetime.datetime(2024, 11, 20, tzinfo=datetime.UTC),
                                     stage=self.stage, number=number)
        except:
            pass

    def create_matches(self, numbers):
        return [self.create_match(number) for number in numbers]

    def test_no_matches(self):
        self.create_matches([])
        context = matches_context(self.tournament, self.stage)
        self.assertEqual(context, {
            "tournament": self.tournament.serialize(),
            "stage": self.stage.serialize(),
            "matches": [],
        })

    def test_one_match(self):
        self.create_matches([1])
        context = matches_context(self.tournament, self.stage)
        self.assertEqual(context, {
            "tournament": self.tournament.serialize(),
            "stage": self.stage.serialize(),
            "matches": [
                {'number': 1,
                 'start_time': datetime.datetime(2024, 11, 20, 0, 0, tzinfo=datetime.timezone.utc)}
            ],
        })

    def test_multiple_matches(self):
        matches = self.create_matches(range(5))
        context = matches_context(self.tournament, self.stage)
        self.assertEqual(context, {
            "tournament": self.tournament.serialize(),
            "stage": self.stage.serialize(),
            "matches": [m.serialize() for m in matches],
        })

    def test_matches_with_same_stage_and_number(self):
        self.create_matches([1, 1])
        context = matches_context(self.tournament, self.stage)
        self.assertEqual(context, {
            "tournament": self.tournament.serialize(),
            "stage": self.stage.serialize(),
            "matches": [
                {'number': 1,
                 'start_time': datetime.datetime(2024, 11, 20, 0, 0, tzinfo=datetime.timezone.utc)}
            ],
        })
