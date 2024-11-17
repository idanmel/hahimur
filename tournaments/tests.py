import datetime
from django.test import TestCase
from django.utils import timezone
from zoneinfo import ZoneInfo

from .models import Match, Stage, Team, Tournament, get_matches


class MatchTests(TestCase):
    def setUp(self):
        t = Tournament.objects.create(name="ASD")
        s = Stage.objects.create(name="A", tournament=t)
        team1 = Team.objects.create(name="Germany")
        team2 = Team.objects.create(name="Scotland")
        Match.objects.create(
            start_time=datetime.datetime(2024, 6, 14, 19, 00, tzinfo=ZoneInfo("UTC")),
            stage=s,
            home_team=team1,
            away_team=team2
        )
        Match.objects.create(
            start_time=datetime.datetime(2024, 6, 15, 19, 00, tzinfo=ZoneInfo("UTC")),
            stage=s,
            home_team=team1,
            away_team=team2
        )
        Match.objects.create(
            start_time=datetime.datetime(2024, 6, 15, 19, 00, tzinfo=ZoneInfo("UTC")),
            stage=s,
            home_team=team1,
            away_team=team2
        )

    def test_zero_matches(self):
        t = Tournament.objects.get(name="ASD")
        matches = get_matches(t.id, year=2020, month=6, day=14)
        self.assertFalse(matches)

    def test_one_match(self):
        t = Tournament.objects.get(name="ASD")
        matches = get_matches(t.id, year=2024, month=6, day=14)
        self.assertEqual(matches[0].stage.tournament.name, "ASD")
        self.assertEqual(matches[0].stage.name, "A")
        self.assertEqual(matches[0].home_team.name, "Germany")
        self.assertEqual(matches[0].away_team.name, "Scotland")
        self.assertEqual(len(matches), 1)

    def test_more_than_one_matches(self):
        t = Tournament.objects.get(name="ASD")
        matches = get_matches(t.id, year=2024, month=6, day=15)
        self.assertEqual(len(matches), 2)
