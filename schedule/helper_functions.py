from schedule.models import AircraftType, Airlines, ScheduleTypes, Stations
from datetime import date, timedelta, datetime


def set_weekday_variables(input_string):
    activityStatus = []
    for i in range(7):
        if str(i + 1) in str(input_string):
            activityStatus.append(True)
        else:
            activityStatus.append(False)
    return activityStatus


def map_excel_data_to_model(excel_data_list, scheduleTypeID):
    mapped_data_list = []
    for excel_data in excel_data_list:
        # # get object ID's
        arrival_airline = Airlines.objects.get(airline_code=excel_data.get('Airline  (Arrival)'),)
        departure_airline = Airlines.objects.get(airline_code=excel_data.get('Airline  (Departure)'),)
        origin_station = Stations.objects.get(station_code=excel_data.get('Origin'),)
        destination_station = Stations.objects.get(station_code=excel_data.get('Destination'),)
        arrival_station = Stations.objects.get(station_code=excel_data.get('Arrival (via)'),)
        departure_station = Stations.objects.get(station_code=excel_data.get('Departure (via)'),)
        aircraft_type = AircraftType.objects.get(aircraft_code=excel_data.get('Aircraft Type'),)
        scheduleType = ScheduleTypes.objects.get(id_schedule_type = scheduleTypeID)
        # check day wise availability
        daysWiseActivity = set_weekday_variables(excel_data.get('Days of Operation'),)
        mapped_data = {
            'id_schedule_type': scheduleType,
            'arrival_airline' :  arrival_airline,
            'departure_airline' :  departure_airline,
            'arrival_flight_no' : excel_data.get('Flight No. (Arrival)'), # or excel_data.get('full_name'),
            'departure_flight_no' : excel_data.get('Flight No. (Departure)'),
            'valid_from' :  excel_data.get('From'),
            'valid_to' :  excel_data.get('To'),
            'sunday_operation' :  daysWiseActivity[0],
            'monday_operation' :  daysWiseActivity[1],
            'tuesday_operation' :  daysWiseActivity[2],
            'wednesday_operation' :  daysWiseActivity[3],
            'thursday_operation' : daysWiseActivity[4],
            'friday_operation' :  daysWiseActivity[5],
            'saturday_operation' : daysWiseActivity[6],
            'origin_station' : origin_station,
            'destination_station' :  destination_station,
            'arrival_station' :  arrival_station,
            'departure_station' :  departure_station,
            'arrival_time' : excel_data.get('Schedule Time (Arrival)'),
            'departure_time' : excel_data.get('Schedule Time (Departure)'),
            'no_of_seats' :  excel_data.get('No. of Seats'),
            'aircraft_type' :  aircraft_type,
            'overnight_parking' :  '',
            'service_type_arrival' : excel_data.get('Service Type - Arr'),
            'service_type_departure' : excel_data.get('Service Type - Dep'),
            }
        mapped_data_list.append(mapped_data)
    return mapped_data_list


def count_flights_by_hour(flights):
    airline_hourly_counts = {}

    for flight in flights:
        id_airline = flight['id_airline']
        airline_name = flight["airline_name"]
        departure_time = int(flight["departure_time"])
        arrival_time = int(flight["arrival_time"])

        for hour in range(24):
            # Calculate the lower and upper bounds of the one-hour slot
            lower_bound = hour * 100
            upper_bound = (hour + 1) * 100

            if lower_bound <= departure_time < upper_bound or lower_bound <= arrival_time < upper_bound:
                key = f"{id_airline}_{airline_name}_{hour:02}"
                if key in airline_hourly_counts:
                    airline_hourly_counts[key] += 1
                else:
                    airline_hourly_counts[key] = 1

    result = []
    for airline_hour, count in airline_hourly_counts.items():
        id_airline, airline_name, hour = airline_hour.split('_')
        hour_int = int(hour)

        found = False
        for item in result:
            if item["airline_name"] == airline_name and item["id_airline"] == id_airline:
                item["date_range"][hour_int]["count"] = count
                found = True
                break

        if not found:
            date_range = [{"date": str(convert_to_time_format(hour)) + ' - ' + str(convert_to_time_format(hour + 1)), "count": 0} for hour in range(24)]
            date_range[hour_int]["count"] = count
            
            result.append({
                "id_airline": id_airline,
                "airline_name": airline_name,
                "date_range": date_range
            })

    return result

def convert_to_time_format(num):
    num_str = str(num)
    
    if len(num_str) == 1:
        return f"0{num_str}:00"
    elif len(num_str) == 2:
        return f"{num_str}:00"
    elif len(num_str) == 3:
        return f"{num_str[0]}{num_str[1]}:{num_str[2]}0"
    elif len(num_str) == 4:
        return f"{num_str[0]}{num_str[1]}:{num_str[2]}{num_str[3]}"
    else:
        return "Invalid input"
    
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def calculate_date_between_range(start_date, end_date):
    try:
        dates = []
        format_string = '%Y-%m-%d'

        start_date = datetime.strptime(start_date, format_string)
        end_date = datetime.strptime(end_date, format_string)
        
        
        while start_date <= end_date:
            dates.append(start_date.strftime(format_string))
            start_date += timedelta(days=1)

        return dates
    except Exception as e:
        # If an error occurs, return an error response
        return e


def convert_to_time_format(number):
    if 0 <= number < 24:
        hours = str(number).zfill(2)
        time_format = f"{hours}:00"
        return time_format
    else:
        return "00:00"
    
def generate_week_intervals(from_date, to_date):
    try:
        from_date = datetime.strptime(from_date, '%Y-%m-%d')
        to_date = datetime.strptime(to_date, '%Y-%m-%d')
        
        week_intervals = []
        
        current_date = from_date
        while current_date <= to_date:
            next_week = current_date + timedelta(days=6)  # End of the week is 6 days away
            week_interval = f"{current_date.strftime('%Y-%m-%d')} / {next_week.strftime('%Y-%m-%d')}"
            week_intervals.append(week_interval)
            current_date = next_week + timedelta(days=1)  # Move to the next week's start
        
        return week_intervals
    except Exception as e:
        # If an error occurs, return an error response
        return e

def build_hour_wise_query(start_date, filter_by, airline_id_tuple):
    base_query = """
        SELECT
            airline.id_airline AS id_airline,
            airline.airline_name AS airline_name,
            airline.airline_code AS airline_code,
            schedule.arrival_time,
            schedule.departure_time,
            schedule.valid_from,
            schedule.valid_to,
            schedule.arrival_airline_id
        FROM
            schedules AS schedule
    """
    
    if filter_by == 'arrival':
        join_condition = "LEFT JOIN airlines AS airline ON schedule.arrival_airline_id = airline.id_airline"
    elif filter_by == 'departure':
        join_condition = "LEFT JOIN airlines AS airline ON schedule.departure_airline_id = airline.id_airline"
    else:
        join_condition = "LEFT JOIN airlines AS airline ON schedule.arrival_airline_id = airline.id_airline OR schedule.departure_airline_id = airline.id_airline"
    print(airline_id_tuple)
    if(airline_id_tuple != ''):
        if filter_by == 'arrival':
            airline_condition = f"AND schedule.arrival_airline_id IN ({airline_id_tuple})"
        elif filter_by == 'departure':
            airline_condition = f"AND schedule.departure_airline_id IN ({airline_id_tuple})"
        else:
            airline_condition = f"""
                AND (
                    schedule.arrival_airline_id IN ({airline_id_tuple}) OR 
                    schedule.departure_airline_id IN ({airline_id_tuple})
                )
            """
    else:
        airline_condition = ''
    full_query = f"""
        {base_query}
        {join_condition}
        WHERE
            (
                schedule.valid_from <= '{start_date}' AND (schedule.valid_to IS NULL OR schedule.valid_to >= '{start_date}')
            )
            AND (
                (EXTRACT(DOW FROM '{start_date}'::date) = 0 AND (schedule.sunday_operation = TRUE OR schedule.sunday_operation IS NULL)) OR
                (EXTRACT(DOW FROM '{start_date}'::date) = 1 AND (schedule.monday_operation = TRUE OR schedule.monday_operation IS NULL)) OR
                (EXTRACT(DOW FROM '{start_date}'::date) = 2 AND (schedule.tuesday_operation = TRUE OR schedule.tuesday_operation IS NULL)) OR
                (EXTRACT(DOW FROM '{start_date}'::date) = 3 AND (schedule.wednesday_operation = TRUE OR schedule.wednesday_operation IS NULL)) OR
                (EXTRACT(DOW FROM '{start_date}'::date) = 4 AND (schedule.thursday_operation = TRUE OR schedule.thursday_operation IS NULL)) OR
                (EXTRACT(DOW FROM '{start_date}'::date) = 5 AND (schedule.friday_operation = TRUE OR schedule.friday_operation IS NULL)) OR
                (EXTRACT(DOW FROM '{start_date}'::date) = 6 AND (schedule.saturday_operation = TRUE OR schedule.saturday_operation IS NULL))
            )
        {airline_condition}
    """
    
    return full_query


def count_no_of_seats_in_flights_by_hour(flights):
    airline_hourly_counts = {}

    for flight in flights:
        id_airline = flight['id_airline']
        airline_name = flight["airline_name"]
        departure_time = int(flight["departure_time"])
        arrival_time = int(flight["arrival_time"])
        no_of_seats = int(flight["no_of_seats"])

        for hour in range(24):
            # Calculate the lower and upper bounds of the one-hour slot
            lower_bound = hour * 100
            upper_bound = (hour + 1) * 100

            if lower_bound <= departure_time < upper_bound or lower_bound <= arrival_time < upper_bound:
                key = f"{id_airline}_{airline_name}_{hour:02}"
                if key in airline_hourly_counts:
                    airline_hourly_counts[key] += no_of_seats
                else:
                    airline_hourly_counts[key] = no_of_seats

    result = []
    for airline_hour, count in airline_hourly_counts.items():
        id_airline, airline_name, hour = airline_hour.split('_')
        hour_int = int(hour)

        found = False
        for item in result:
            if item["airline_name"] == airline_name and item["id_airline"] == id_airline:
                item["date_range"][hour_int]["count"] = count
                found = True
                break

        if not found:
            date_range = [{"date": str(convert_to_time_format(hour)) + ' - ' + str(convert_to_time_format(hour + 1)), "count": 0} for hour in range(24)]
            date_range[hour_int]["count"] = count
            
            result.append({
                "id_airline": id_airline,
                "airline_name": airline_name,
                "date_range": date_range
            })

    return result
