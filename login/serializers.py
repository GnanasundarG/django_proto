# myapp/serializers.py

from rest_framework import serializers
from login.models import role, users
class HelloSerializer(serializers.Serializer):
    msg = serializers.CharField(max_length=100)

    def to_representation(self, instance):
        return { "msg": instance.get('msg', 'Hello') }

    def validate_msg(self, value):
        if not value:
            raise serializers.ValidationError("The 'msg' field is required.")
        return value
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model=role 
        fields='__all__'
class UserSerializer(serializers.ModelSerializer):

  class Meta:
        model=users 
        fields= '__all__'        
