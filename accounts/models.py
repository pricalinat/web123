from django.db import models


# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=10, unique=True)
    password = models.CharField(max_length=256)
    student_id = models.CharField(max_length=10, unique=True, default="0000000000")
    team = models.ForeignKey(  # 多个用户对一个team "team_id"
        'Team',
        related_name='members',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
    )
    point = models.IntegerField(default=0)

    # solved_challenges = models.Many ToManyField("Challenges") # 多对多

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'person'
        verbose_name_plural = 'people'
        ordering = ['-point']


class BaseInfo(models.Model):
    baseName = models.CharField(max_length=10, unique=True)
    baseId = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.baseName


class Team(models.Model):
    team_name = models.CharField(max_length=20, unique=True, default=None, null=True)
    team_number = models.IntegerField(default=1)

    # 人数上限为3人
    team_leader = models.CharField(max_length=10, unique=True, default=None)  # 队长名字
    point = models.IntegerField(default=0)

    def __str__(self):
        return self.team_name

    class Meta:
        ordering = ['-point']
