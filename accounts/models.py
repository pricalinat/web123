from django.db import models


# Create your models here.


class User(models.Model):
    name = models.CharField(max_length=10, unique=True)
    password = models.CharField(max_length=256)
    student_id = models.CharField(max_length=10, unique=True, default="0000000000")
    email = models.EmailField(unique=True, default='1111@123.com')
    team = models.ForeignKey(  # 多个用户对一个team "team_id"
        'Team',
        related_name='members',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
    )
    point = models.IntegerField(default=0)
    has_confirmed = models.BooleanField(default=False)
    # Challenges = get_challenges()
    # collections = models.ManyToManyField(Challenges)  # 多对多

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


class ConfirmString(models.Model):
    code = models.CharField(max_length=256)
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.name + ":   " + self.code

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "confirm_code"
        verbose_name_plural = "confirm_code"


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


class Suggestion(models.Model):
    user_name = models.CharField(max_length=4, default=None)
    suggestion = models.CharField(max_length=100, default=None)

    def __str__(self):
        return '来自' + self.user_name
