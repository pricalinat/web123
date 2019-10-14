from django.db import models

# Create your models here.
class Team(models.Model):
    team_name = models.CharField(max_length=20, unique=True,default='31class')
    team_number= models.IntegerField(default=1)  # 人数上限为3人

    def __str__(self):
        return self.team_name
