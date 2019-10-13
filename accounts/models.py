from django.db import models


# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=10, unique=True)
    password = models.CharField(max_length=256)
    student_id = models.CharField(max_length=10, unique=True,default="0000000000")
    # team = models.ForeignKey(  # 多个用户对一个team "team_id"
    #     'Team',
    #     on_delete=models.CASCADE,
    #     null=True,
    #     blank=True,
    #     default=None,
    # )

    # solved_challenges = models.ManyToManyField("Challenges") # 多对多

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'


class Team(models.Model):
    team_name = models.CharField(max_length=10, unique=True)
    player_number = models.IntegerField(default=0)  # 人数上限为3人

    def __str__(self):
        return self.team_name


class BaseInfo(models.Model):
    baseName = models.CharField(max_length=10, unique=True)
    baseId = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.baseName
