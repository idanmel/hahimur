from django.db import models

# matches
# results
# users
# user scores
# teams

class Tournament(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.name}'

class Team(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.name}'

class Match(models.Model):
    start_time = models.DateTimeField()
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away')

    def __str__(self):
        return f'{self.home_team} - {self.away_team} at {self.start_time}'
