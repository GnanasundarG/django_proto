from django.db import models

class Airlines(models.Model):
    id_airline = models.AutoField(primary_key=True)
    airline_code = models.TextField()
    airline_name = models.TextField()
    logo_image = models.TextField(default='')

    def __str__(self):
        return self.airline_name
    class Meta:
        db_table = "airlines"

class Stations(models.Model):
    id_station = models.IntegerField(primary_key=True)
    station_name = models.TextField()
    station_code = models.TextField()
    country=models.TextField(default='')
    station_logo= models.TextField(default='')
    def __str__(self):
        return self.station_name
    class Meta:
        db_table = "stations"

class AircraftType(models.Model):
    id_aircraft_type = models.IntegerField(primary_key=True)
    aircraft_name = models.TextField()
    aircraft_code = models.TextField()
    aircraft_logo = models.TextField(default='')
    aircraft_type = models.TextField(default='')
    def __str__(self):
        return self.aircraft_name
    class Meta:
        db_table = "aircraft_types"
        
class ScheduleTypes(models.Model):
    id_schedule_type = models.AutoField(primary_key=True)
    schedule_type_name = models.TextField()

    def __str__(self):
        return self.airline_name
    class Meta:
        db_table = "schedule_types"


class Schedules(models.Model):
    id_schedule = models.AutoField(primary_key=True)
    id_schedule_type = models.ForeignKey(ScheduleTypes, on_delete=models.CASCADE, related_name='schedule_types')
    arrival_airline = models.ForeignKey(Airlines, on_delete=models.CASCADE, related_name='arrival_schedules')
    departure_airline = models.ForeignKey(Airlines, on_delete=models.CASCADE, related_name='departure_schedules')
    arrival_flight_no = models.TextField()
    departure_flight_no = models.TextField()
    valid_from = models.DateField()
    valid_to = models.DateField()
    monday_operation = models.BooleanField()
    tuesday_operation = models.BooleanField()
    wednesday_operation = models.BooleanField()
    thursday_operation = models.BooleanField()
    friday_operation = models.BooleanField()
    saturday_operation = models.BooleanField()
    sunday_operation = models.BooleanField()
    origin_station = models.ForeignKey(Stations, on_delete=models.CASCADE, related_name='origin_schedules')
    destination_station = models.ForeignKey(Stations, on_delete=models.CASCADE, related_name='destination_schedules')
    arrival_station = models.ForeignKey(Stations, on_delete=models.CASCADE, related_name='arrival_schedules')
    departure_station = models.ForeignKey(Stations, on_delete=models.CASCADE, related_name='departure_schedules')
    arrival_time = models.TextField()
    departure_time = models.TextField()
    no_of_seats = models.IntegerField()
    aircraft_type = models.ForeignKey(AircraftType, on_delete=models.CASCADE, related_name='schedules')
    overnight_parking = models.BooleanField(null=True, blank=True)
    service_type_arrival = models.TextField()
    service_type_departure = models.TextField()

    def __str__(self):
        return f"Schedule {self.id_schedule}"
    class Meta:
        db_table = "schedules"
