from django.db import models
from django.contrib.auth.models import User

class Request(models.Model):
    details = models.CharField(max_length = 500)
    room = models.CharField(max_length = 3)
    event = models.CharField(max_length = 10)
    requested_by = models.CharField(max_length=20)
    date = models.DateField(null = True)
    from_ts = models.TimeField()
    to_ts = models.TimeField()

    def __str__(self):
        return self.room
