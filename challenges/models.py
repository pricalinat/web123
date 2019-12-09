from django.db import models
from accounts.models import User
import hashlib


# Create your models here.

def get_upload_path(instance, filename):
    return str(instance.category) + '/challenges_{0}/{1}'.format(hashlib.md5(instance.name.encode('utf-8')).hexdigest(),
                                                            filename)


CATEGORY_CHOICES = ((0, 'RE'), (1, 'WEB'), (2, 'PWN'))


class Challenges(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.IntegerField(choices=CATEGORY_CHOICES)
    message = models.CharField(max_length=1000, blank=True, default="")
    point = models.IntegerField(default=0)
    file = models.FileField(null=True, blank=True, upload_to=get_upload_path)
    flag = models.CharField(max_length=100)
    scene = models.CharField(default=None, max_length=100)
    solver = models.ManyToManyField(User,
                                    blank=True,
                                    default=None,
                                    related_name='solve')
    collector = models.ManyToManyField(User,
                                    blank=True,
                                    default=None,
                                    related_name='collect')

    class Meta:
        verbose_name = 'challenge'
        verbose_name_plural = 'challenges'

    def __str__(self):
        return self.name
