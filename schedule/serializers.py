
from rest_framework import serializers
from schedule.models import Airlines, Schedules, ScheduleTypes


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model= Schedules
        fields='__all__'

 
class AirlinesSerializer(serializers.ModelSerializer):
    class Meta:
        model= Airlines
        fields='__all__'

class ScheduleTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model=ScheduleTypes 
        fields='__all__'

    