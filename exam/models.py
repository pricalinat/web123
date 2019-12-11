from django.db import models
from accounts.models import User
from challenges.models import Challenges
import datetime

# Create your models here.
class Exam(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    problems = models.ManyToManyField(Challenges, default=None)
    point = models.IntegerField(default=0)
    full_marks = models.IntegerField(default=0)
    start_time = models.DateTimeField(default=datetime.datetime.now())


    def __str__(self):
        return self.user.name+'的考试'