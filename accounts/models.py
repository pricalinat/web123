from django.db import models


# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=10, unique=True)
    password = models.CharField(max_length=256)
    points = models.IntegerField(default=0)
    # student_id = models.CharField(max_length=10, unique=True)
    # team = models.ForeignKey(  # 多个用户对一个team
    #     'Team',
    #     on_delete=models.CASCADE,
    # )

    # solved_challenges = models.ManyToManyField("Challenges") # 多对多

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['points']
        verbose_name = '用户'
        verbose_name_plural = '用户'


class Team(models.Model):
    team_name = models.CharField(max_length=10, unique=True)
    player_number = models.IntegerField(default=0)  # 人数上限为3人

    def __str__(self):
        return self.team_name
