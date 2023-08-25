from django.db import models

from schedule.models import Stations

class role(models.Model):
    id_role = models.AutoField(primary_key=True)
    role_code = models.CharField(max_length=500)
    role_name = models.CharField(max_length=500)

    class Meta:  
        db_table = "role" 

class users(models.Model):
    id_user = models.AutoField(primary_key=True)
    username = models.CharField(max_length=500)
    role = models.ForeignKey(role, on_delete=models.PROTECT, related_name='users')
    email=models.TextField(max_length=500)
    password = models.TextField(max_length=500)
    station = models.ForeignKey(Stations, on_delete=models.PROTECT, related_name='users', default='', null=True)
    class Meta:
        db_table = "users"