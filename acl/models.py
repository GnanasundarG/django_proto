from django.db import models
from login.models import role

# Create your models here.
class api_url(models.Model):
    id_api_url = models.AutoField(primary_key=True)
    api_url = models.CharField(max_length=500)

    class Meta:  
        db_table = "api_url" 

class api_url_access(models.Model):
    id_api_url_access = models.AutoField(primary_key=True)
    role = models.ForeignKey(role, on_delete=models.PROTECT, related_name='api_url_access')
    get = models.BooleanField(default=False)
    post = models.BooleanField(default=False)
    patch = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)
    url = models.ForeignKey(api_url, on_delete=models.PROTECT, related_name='access_details')

    class Meta:  
        db_table = "api_url_access"
