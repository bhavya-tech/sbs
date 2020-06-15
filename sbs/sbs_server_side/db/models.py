from django.db import models
from django.contrib.auth.models import User

#this object will be used for database
#
class Record(models.Model):
    details = models.CharField(max_length = 500)
    room = models.CharField(max_length = 3)
    event = models.CharField(max_length = 10)
    requested_by = models.CharField(max_length=20)
    from_ts = models.DateTimeField(primary_key = True)
    to_ts = models.DateTimeField()
    accepted = models.BooleanField(null = True)

    def __str__(self):
        return self.room + " " + self.from_ts + " " + self.to_ts

class UserProfileInfo(models.Model):
    #usname,paaswd,is_admin
    user = models.OneToOneField(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
