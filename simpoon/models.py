from django.db import models


class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=10, verbose_name="유저 이름")
    email = models.CharField(max_length=200, verbose_name="e-mail")
