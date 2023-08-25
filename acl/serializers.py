


from acl.models import api_url, api_url_access
from rest_framework import serializers


class ApiUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model=api_url 
        fields='__all__'


class ApiUrlAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model=api_url_access 
        fields='__all__'