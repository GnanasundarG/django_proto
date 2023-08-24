from django.urls import path

from . import views

urlpatterns = [
    path('scheduleUpload/', views.scheduleUpload, name='upload_schedule'),
    path('airlinesUpload/', views.airlinesUpload, name='upload_airlines'),
    path('getScheduleTypes/', views.getScheduleTypes, name='get schedule types'),
    path('getHighlights/', views.get_schedules_highlights, name='get schedule highlights'),
    path('isScheduleDataExist/', views.is_schedule_data_exist, name='check the schedules data ia already uploaded or not'),
    # path('getAirlineReport/', views.airline_schedule_report, name='get airline reports'),
    path('getairlines/', views.airlinesApi, name='get_airlines'),
    path('getscheduleairlines', views.airline_data_api, name='get_airlines_filtered'),
    path('getAirlineReport/', views.airline_schedule_report, name='get airline reports'),
    path('getoriginairlines/', views.OriginBasedAirlineswise, name='get_origin_airlines'),
    path('getdestinationairlines/', views.DestinationBasedAirlineswise, name='get_destination_airlines'),
    path('getairlinesovernightparkingcount', views.aircraftBasedOvernightParkingCount, name='get_airlines_seats'),
    path('getairlineseatcount', views.aircraftBasedAirlinesSeatCount, name='get_airlines_seats'),
    path('getairlinepaxhandlingreport/', views.airline_paxhandling_report, name='airline_paxhandling_report'),
    path('getairlineslist', views.getAirlinesList, name='get_airlines_list'),
    path('getaircraftslist', views.getAircraftsList, name='get_aircrafts_list'),

    path('airlinearrivalsdeparturesreport/', views.airline_arrivalsdepartures_report, name='airline_arrivalsdepartures_report')
]

