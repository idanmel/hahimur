from django.test import TestCase

### So let's start with the tournament matches view?
### So what are our tests?
### Show no matches.
### Show a match that wasn't played yet.
### Show a match that was already played.
### Show a list of matches.
 

class MatchTests(TestCase):
    def test_zero_matches(self):
        t = Tournament.objects.get(name="ASD")
        matches = get_matches(t)
        self.assertFalse(matches)