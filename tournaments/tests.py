import datetime

from django.db import IntegrityError
from django.test import TestCase, TransactionTestCase
from django.utils.timezone import make_aware

from tournaments.models import Match, Stage, Tournament


def get_matches(t):
    return Match.objects.filter(stage__tournament=t)


def create_matches(numbers):
    t = Tournament.objects.create(name="ASD")
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


def create_tournament(tid, name):
    try:
        Tournament.objects.create(id=tid, name=name)
    except IntegrityError:
        pass


def create_tournaments(tournaments_data):
    for tid, name in tournaments_data:
        create_tournament(tid, name)


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
