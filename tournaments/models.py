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