import datetime

from django.db import IntegrityError
from django.test import TestCase, TransactionTestCase
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


def serialize_tournament(t):
    return {
        "id": t.id,
        "name": t.name,
    }


def get_tournaments():
    ts = Tournament.objects.all()
    serialized = [serialize_tournament(t) for t in ts]
    return {"tournaments": serialized}


class TournamentsTest(TransactionTestCase):
    def test_no_tournaments(self):
        create_tournaments([])
        context = get_tournaments()
        self.assertEqual(context, {"tournaments": []})

    def test_one_tournament(self):
        create_tournaments([(1, "Euro 2024")])
        context = get_tournaments()
        self.assertEqual(context, {"tournaments": [{"id": 1, "name": "Euro 2024"}]})

    def test_multiple_tournament(self):
        create_tournaments([(1, "Euro 2024"), (2, "Euro 2025"), (3, "World Cup 3012")])
        context = get_tournaments()
        self.assertEqual(context, {
            "tournaments": [
                {"id": 1, "name": "Euro 2024"},
                {"id": 2, "name": "Euro 2025"},
                {"id": 3, "name": "World Cup 3012"},
            ]
        })

    def test_same_tournament_name_twice(self):
        create_tournaments([(1, "Euro 2024"), (2, "Euro 2024")])
        context = get_tournaments()
        self.assertEqual(context, {"tournaments": [{"id": 1, "name": "Euro 2024"}]})


def serialize_stage(s):
    return {"stage_id": s.id, "name": s.name}


def stages_context(t):
    stages = Stage.objects.filter(tournament=t)
    return {"Tournament": serialize_tournament(t), "stages": [serialize_stage(s) for s in stages]}


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
        self.assertEqual(context, {"Tournament": serialize_tournament(self.tournament), "stages": stages})

    def test_one_stage(self):
        stages = [
            {"stage_id": 1, "name": "Group A"}
        ]
        context = self.get_test_stages(stages)
        self.assertEqual(context, {"Tournament": serialize_tournament(self.tournament), "stages": stages})

    def test_multiple_stages(self):
        stages = [
            {"stage_id": 1, "name": "Group A"},
            {"stage_id": 2, "name": "Group B"},
            {"stage_id": 3, "name": "Round of 16"}
        ]
        context = self.get_test_stages(stages)
        self.assertEqual(context,{
            "Tournament": serialize_tournament(self.tournament),
            "stages": stages
        })

    def test_unique_stages(self):
        stages = [
            {"stage_id": 1, "name": "Group A"},
            {"stage_id": 2, "name": "Group A"},
        ]
        context = self.get_test_stages(stages)
        self.assertEqual(context, {
            "Tournament": serialize_tournament(self.tournament),
            "stages": [{"stage_id": 1, "name": "Group A"}]
        })


class TournamentTest(TestCase):
    def test_no_matches(self):
        t = create_matches(range(0))
        matches = get_matches(t)
        self.assertFalse(matches)

    def test_one_match(self):
        t = create_matches(range(1, 2))
        matches = get_matches(t)
        self.assertEqual(len(matches), 1)

    def test_multiple_matches(self):
        t = create_matches(range(1, 5))
        matches = get_matches(t)
        self.assertEqual(len(matches), 4)

    # def test_matches_with_same_stage_and_number(self):
    #     t = create_tournament([1])
    #     try:
    #         t = create_tournament([1])
    #     except:
    #         pass
    #     matches = get_matches(t)
    #     self.assertEqual(len(matches), 1)
