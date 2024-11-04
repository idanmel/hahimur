from django.db import models

# Create your models here.

class Tournament(models.Model):
    name = models.CharField(max_length=200)


# tournaments
# matches
# results
# users
# user scores
# teams
