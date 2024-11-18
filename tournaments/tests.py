import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from tournaments.models import Match, Stage, Tournament


def get_matches(t):
    return Match.objects.filter(stage__tournament=t)


def create_tournament(numbers):
    t = Tournament.objects.create(name="ASD")
    stage = Stage.objects.create(name="123", tournament=t)
    for number in numbers:
        Match.objects.create(
            start_time=make_aware(datetime.datetime.now()),
            stage=stage,
            number=number
        )
    return t


class TournamentTest(TestCase):
    def test_no_matches(self):
        t = create_tournament(range(0))
        matches = get_matches(t)
        self.assertFalse(matches)

    def test_one_match(self):
        t = create_tournament(range(1, 2))
        matches = get_matches(t)
        self.assertEqual(len(matches), 1)

    def test_multiple_matches(self):
        t = create_tournament(range(1, 5))
        matches = get_matches(t)
        self.assertEqual(len(matches), 4)

    def test_matches_with_same_stage_and_number(self):
        t = create_tournament([1, 1])
        matches = get_matches(t)
        self.assertFalse(matches)
