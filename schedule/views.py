from datetime import timedelta, timezone
import json

import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import connection
from collections import defaultdict
from datetime import timedelta, datetime

from login.response_utils import generate_error_response, manual_error_response
from rest_framework.decorators import api_view
from schedule.helper_functions import build_hour_wise_query, convert_to_time_format, count_flights_by_hour, map_excel_data_to_model, calculate_date_between_range, generate_week_intervals
from schedule.models import AircraftType, Airlines, Schedules, ScheduleTypes
from schedule.serializers import ScheduleTypesSerializer


from django.http import JsonResponse
from django.db import connection
from datetime import date, datetime, timedelta
from django.utils import timezone
from datetime import datetime
from collections import defaultdict

from functools import reduce
from django.db.models.functions import ExtractHour
from django.db.models import Count
from django.db.models import F, Func, Value, IntegerField

@csrf_exempt
@api_view(['POST'])
# @renderer_classes((TemplateHTMLRenderer, JSONRenderer))
# @validate_schedule_upload
def scheduleUpload(request):
    try:
        if request.method == 'POST' and 'file' in request.FILES:
            scheduletypeid = request.GET.get('scheduletypeid')
            file = request.FILES['file']
            # Read the Excel file into a pandas DataFrame
            df = pd.read_excel(file)

            # Convert the DataFrame to a list of dictionaries (to use orient='records')
            records = df.to_dict(orient='records')
            print(records)
            ScheduleRecords = map_excel_data_to_model(records, scheduletypeid)
            for record in ScheduleRecords:
                airline = Schedules(**record)
                airline.save()
            # Return the data as the API response
            return JsonResponse({ 'success' : True ,'message': 'Records added successfully'}, safe=False)
        return manual_error_response(400, 'Invalid request', "")
    except Exception as e:
        # Call the updated generate_error_response function with the exception as argument
        return generate_error_response(e)


@csrf_exempt
def airlinesUpload(request):
    if request.method == 'GET':
        airlines = Airlines.objects.all()
        data = [{"code": airline.code, "name": airline.name} for airline in airlines]
        return JsonResponse(data, safe=False)
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)  # Parse the JSON data from the request body
            
            for code, name in data.items():
                airline = Airlines(airline_code=code, airline_name=name)
                airline.save()
            
            return JsonResponse({'success' : True ,"message": "Airlines added successfully"}, status=201)
        except json.JSONDecodeError:
            return manual_error_response(400, 'Invalid JSON data', "")
        except KeyError:
            return manual_error_response(400, "Invalid data. Each item should have 'code' and 'name'.',")
        

@api_view(['GET'])
def getScheduleTypes(request):
    if request.method=='GET':
        types = ScheduleTypes.objects.all()
        typeSerializers = ScheduleTypesSerializer(types,many=True)
    try:
     return JsonResponse({'message': 'Fetched Schedule Types successfully','success':True,'respayload':typeSerializers.data,},safe=False)
    except Exception as e:
        # Call the updated generate_error_response function with the exception as argument
        return generate_error_response(e)

@csrf_exempt
@api_view(['POST'])
def aircraftTypeUpload(request):
    if request.method == 'GET':
        aircraftType = AircraftType.objects.all()
        data = [{"code": airline.code, "name": airline.name} for airline in aircraftType]
        return JsonResponse(data, safe=False)
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)  # Parse the JSON data from the request body
            for code, name in data.items():
                aircraftType = AircraftType(airline_code=code, airline_name=name)
                aircraftType.save()
            return JsonResponse({"message": "AircraftType added successfully"}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except KeyError:
            return JsonResponse({"error": "Invalid data. Each item should have 'code' and 'name'."}, status=400)
        
        
@api_view(['GET'])
def get_schedules_highlights(request):
    try:
        current_date = request.GET.get('date')
        
        if not current_date:
        # If current_date is not available, fetch the minimum date from the schedules table
            with connection.cursor() as cursor:
                cursor.execute("SELECT MIN(valid_from) FROM schedules;")
                result = cursor.fetchone()
                min_date = result[0] if result[0] else date.today().isoformat()
                current_date = min_date

        # Define the SQL query to fetch data from the database
        sql_query = f"""
            SELECT COUNT(DISTINCT arrival_airline_id) as airlines, COUNT(*) as total_schedules, SUM(no_of_seats) as total_seats
            FROM schedules WHERE schedules.valid_from <= '{current_date}' AND (schedules.valid_to IS NULL OR schedules.valid_to >= '{current_date}')
            AND (
            (EXTRACT(DOW FROM '{current_date}'::date) = 0 AND (schedules.sunday_operation = TRUE OR schedules.sunday_operation IS NULL)) OR
            (EXTRACT(DOW FROM '{current_date}'::date) = 1 AND (schedules.monday_operation = TRUE OR schedules.monday_operation IS NULL)) OR
            (EXTRACT(DOW FROM '{current_date}'::date) = 2 AND (schedules.tuesday_operation = TRUE OR schedules.tuesday_operation IS NULL)) OR
            (EXTRACT(DOW FROM '{current_date}'::date) = 3 AND (schedules.wednesday_operation = TRUE OR schedules.wednesday_operation IS NULL)) OR
            (EXTRACT(DOW FROM '{current_date}'::date) = 4 AND (schedules.thursday_operation = TRUE OR schedules.thursday_operation IS NULL)) OR
            (EXTRACT(DOW FROM '{current_date}'::date) = 5 AND (schedules.friday_operation = TRUE OR schedules.friday_operation IS NULL)) OR
            (EXTRACT(DOW FROM '{current_date}'::date) = 6 AND (schedules.saturday_operation = TRUE OR schedules.saturday_operation IS NULL))
        );

        """

        # Execute the SQL query
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            result = cursor.fetchone()

        airlinesCount = result[0]
        total_schedules = result[1]
        total_hours = result[2]

        response_data = {
            'success': True,
            'message': 'Data fetched successfully',
            'respayload': {
                'airlines': airlinesCount,
                'schedules': total_schedules,
                'noOfSeats': total_hours,
                'current_date': current_date
            }
        }

        return JsonResponse(response_data)
    except Exception as e:
        # Call the updated generate_error_response function with the exception as argument
        return generate_error_response(e)
        
@api_view(['GET'])
def is_schedule_data_exist(request):
    try:
        # Perform the query to check if data exists
        data_exists = Schedules.objects.exists()

        # Return True if data exists, False otherwise
        response_data = {'data_exists': data_exists ,'message': 'schdule is checked'}
        return JsonResponse(response_data)

    except Exception as e:
        # If an error occurs, return an error response
        return generate_error_response(e)

@api_view(['GET'])
@csrf_exempt
def airline_data_api(request):
    current_date = datetime.now().date()
    current_day_of_week = current_date.isoweekday()

    # Extract airline names from the URL parameters
    airline_names = request.GET.getlist('airline_name', [''])

    # Extract valid_from and valid_to dates from the URL parameters
    valid_from_str = request.GET.get('valid_from')
    valid_to_str = request.GET.get('valid_to')

    # Convert valid_from and valid_to strings to date objects
    valid_from = datetime.strptime(valid_from_str, '%Y-%m-%d').date() if valid_from_str else current_date
    valid_to = datetime.strptime(valid_to_str, '%Y-%m-%d').date() if valid_to_str else current_date

    # Create placeholders for the airline_names to use in the SQL query
    placeholders = ','.join(['%s'] * len(airline_names))

    with connection.cursor() as cursor:
        query = """
            SELECT
                a.airline_name,
                COUNT(DISTINCT CASE WHEN s_arrival.valid_from <= %s AND s_arrival.valid_to >= %s AND 
                    CASE %s
                        WHEN 1 THEN s_arrival.monday_operation
                        WHEN 2 THEN s_arrival.tuesday_operation
                        WHEN 3 THEN s_arrival.wednesday_operation
                        WHEN 4 THEN s_arrival.thursday_operation
                        WHEN 5 THEN s_arrival.friday_operation
                        WHEN 6 THEN s_arrival.saturday_operation
                        WHEN 7 THEN s_arrival.sunday_operation
                    END
                THEN s_arrival.id_schedule END) AS arrival_count,
                COUNT(DISTINCT CASE WHEN s_departure.valid_from <= %s AND s_departure.valid_to >= %s AND 
                    CASE %s
                        WHEN 1 THEN s_departure.monday_operation
                        WHEN 2 THEN s_departure.tuesday_operation
                        WHEN 3 THEN s_departure.wednesday_operation
                        WHEN 4 THEN s_departure.thursday_operation
                        WHEN 5 THEN s_departure.friday_operation
                        WHEN 6 THEN s_departure.saturday_operation
                        WHEN 7 THEN s_departure.sunday_operation
                    END
                THEN s_departure.id_schedule END) AS departure_count,
                COUNT(DISTINCT CASE WHEN s.valid_from <= %s AND s.valid_to >= %s AND s.overnight_parking AND 
                    CASE %s
                        WHEN 1 THEN s.monday_operation
                        WHEN 2 THEN s.tuesday_operation
                        WHEN 3 THEN s.wednesday_operation
                        WHEN 4 THEN s.thursday_operation
                        WHEN 5 THEN s.friday_operation
                        WHEN 6 THEN s.saturday_operation
                        WHEN 7 THEN s.sunday_operation
                    END
                THEN s.id_schedule END) AS overnight_parking_count
            FROM airlines a
            LEFT JOIN schedules s_arrival ON a.id_airline = s_arrival.arrival_airline_id
            LEFT JOIN schedules s_departure ON a.id_airline = s_departure.departure_airline_id
            LEFT JOIN schedules s ON a.id_airline = s.arrival_airline_id OR a.id_airline = s.departure_airline_id
            WHERE (%s = '' OR a.airline_name IN ({})) AND EXISTS (
                SELECT 1 FROM schedules WHERE (arrival_airline_id = a.id_airline OR departure_airline_id = a.id_airline)
                    AND (%s BETWEEN valid_from AND valid_to OR %s BETWEEN valid_from AND valid_to OR valid_from >= %s)
            )
            GROUP BY a.airline_name
        """

        # Build a list of all arguments required for the query
        args = [valid_from, valid_to, current_day_of_week, valid_from, valid_to, current_day_of_week,
                valid_from, valid_to, current_day_of_week]
        args.extend(airline_names)
        args.extend([airline_names[0], valid_from, valid_to, valid_from])

        cursor.execute(query.format(placeholders), args)

        rows = cursor.fetchall()
        airlines_data = []

        for row in rows:
            airline_name, arrival_count, departure_count, overnight_parking_count = row

            # Exclude the airline data if all counts are 0
            if arrival_count > 0 or departure_count > 0 or overnight_parking_count > 0:
                airlines_data.append({
                    "airline_name": airline_name,
                    "arrival_count": arrival_count,
                    "departure_count": departure_count,
                    "overnight_parking_count": overnight_parking_count
                })

    response_data = {
        "success": True,
        "respayload": airlines_data,
        "message": "airlines data is fetched successfully"
    }

    return JsonResponse(response_data, safe=False)

@csrf_exempt
def airlinesApi(request):
    try:
        if request.method=='GET':

            with connection.cursor() as cursor:
                query = """
                    SELECT id_airline, airline_name, airline_code, logo_image FROM airlines a
                    RIGHT JOIN schedules s ON a.id_airline = s.arrival_airline_id OR a.id_airline = s.departure_airline_id
                    GROUP BY a.id_airline
                """

                cursor.execute(query)

                rows = cursor.fetchall()
                airlines_data = []

                for row in rows:
                    id_airline, airline_name, airline_code, logo_image = row

                    airlines_data.append({
                            "id_airline": id_airline,
                            "airline_code": airline_code,
                            "airline_name": airline_name,
                            "logo_image": logo_image
                        })

        return JsonResponse({'message': 'Fetched Airlines successfully','success':True,'respayload':airlines_data,},safe=False)
    
    except Exception as e:
        # Call the updated generate_error_response function with the exception as argument
        return generate_error_response(e)


@api_view(['GET'])
def airline_schedule_report(request):
    valid_from = request.GET.get('valid_from')
    valid_to = request.GET.get('valid_to')
    airline_id = request.GET.getlist('airline_id', [])
    day_wise = request.GET.get('day_wise').lower() == 'true'
    filter_by = request.GET.get('filter_by')
    start_date = ''
    end_date = ''
    date_query = ''
    airline_id_query = ''
    format_string = '%Y-%m-%d'
    interval_type = ""

    airline_id_tuple = ', '.join(str(id) for id in airline_id)
    print(type(day_wise))
    # calculating dates for getting the schedule date 
    if not valid_from and not valid_to:
        with connection.cursor() as cursor:
            cursor.execute("SELECT MIN(valid_from) FROM schedules;")
            result = cursor.fetchone()
            min_date = result[0].strftime(format_string) if result[0] else date.today().strftime(format_string)
            start_date = min_date
            end_date = min_date
    elif not valid_from or not valid_to:
        start_date = valid_from if not valid_to else valid_to
        end_date = valid_from if not valid_to else valid_to
    elif valid_from and valid_to:
        start_date = valid_from
        end_date = valid_to

    # calculating date range for individual dates
    date_array = calculate_date_between_range(start_date, end_date)

    # forming queries
    # forming the date query to be appended for day wise query execution
    for index, curr_date in enumerate(date_array):
        if index == 0:
            date_query = date_query + f"SELECT '{curr_date}'::date AS custom_date"
            if len(date_array) > 1:
                date_query = date_query + " UNION ALL"
        elif index == len(date_array) - 1:
            date_query = date_query + f" SELECT '{curr_date}'::date"
        else:
            date_query = date_query + f" SELECT '{curr_date}'::date UNION ALL"

    #forming airline query
    for airline_index, curr_id in enumerate(airline_id):
        if airline_index == 0:
            airline_id_query = airline_id_query + f" WHERE id_airline IN ({curr_id}"
            if len(airline_id) <= 1:
                airline_id_query = airline_id_query + ")"
        elif airline_index == len(airline_id) - 1:
            airline_id_query = airline_id_query + f",{curr_id})"
        else:
            airline_id_query = airline_id_query + f",{curr_id}"
            
    if filter_by == 'arrival':
        join_condition = "LEFT JOIN airlines AS airline ON schedules.arrival_airline_id = airline.id_airline"
    elif filter_by == 'departure':
        join_condition = "LEFT JOIN airlines AS airline ON schedules.departure_airline_id = airline.id_airline"
    else:
        join_condition = "LEFT JOIN airlines AS airline ON schedules.arrival_airline_id = airline.id_airline OR schedules.departure_airline_id = airline.id_airline"

    day_wise_query = """
        WITH RECURSIVE date_range AS (
            SELECT 
                id_schedule,
                CAST(valid_from AS timestamp) as date_value
            FROM
                schedules
            UNION ALL
            SELECT
                dr.id_schedule,
                dr.date_value + INTERVAL '1' DAY
            FROM
                date_range dr
            JOIN
                schedules s ON dr.id_schedule = s.id_schedule
            WHERE
                dr.date_value < (SELECT MAX(CAST(valid_to AS date)) FROM schedules WHERE id_schedule = dr.id_schedule)
        ),
        custom_date_range AS (%s),
        individual_schedule AS (
            SELECT
                schedules.id_schedule,
                CAST(schedules.valid_from AS timestamp) AS valid_from_timestamp,
                CAST(schedules.valid_to AS timestamp) AS valid_to_timestamp,
                airline.airline_name,
                airline.id_airline,
                generate_series(CAST(schedules.valid_from AS timestamp), CAST(schedules.valid_to AS timestamp), '1 day')::date AS date_value
            FROM
                schedules
            %s
            %s
        )
        SELECT
            t.id_airline,
            t.airline_name,
            json_agg(json_build_object( 'date', date_value, 'count', event_count) ORDER BY date_value) AS date_range
        FROM (
            SELECT
                v.id_airline,
                v.airline_name,
                date_value,
                COUNT(date_value) AS event_count
            FROM
                custom_date_range c
            CROSS JOIN
                (SELECT DISTINCT id_schedule, id_airline, airline_name, valid_from_timestamp, valid_to_timestamp FROM individual_schedule) v
            LEFT JOIN individual_schedule i ON c.custom_date = i.date_value AND v.id_schedule = i.id_schedule AND v.id_airline = i.id_airline
            WHERE
                i.date_value BETWEEN v.valid_from_timestamp::date AND v.valid_to_timestamp::date
            GROUP BY
                v.id_airline, date_value, v.airline_name
        ) AS t
        GROUP BY
            t.id_airline, t.airline_name
        ORDER BY
            t.id_airline

    """

    # airline_condition = f"""
    #     AND (
    #         schedule.arrival_airline_id IN ({airline_id_tuple}) OR 
    #         schedule.departure_airline_id IN ({airline_id_tuple})
    #     )
    # """
    # hour_wise_query = f"""
    #         SELECT
    #             airline.id_airline AS id_airline,
    #             airline.airline_name AS airline_name,
    #             airline.airline_code AS airline_code,
    #             schedule.arrival_time,
    #             schedule.departure_time,
    #             schedule.valid_from,
    #             schedule.valid_to,
    #             schedule.arrival_airline_id
    #         FROM
    #             schedules AS schedule
    #         LEFT JOIN airlines AS airline ON schedule.arrival_airline_id = airline.id_airline OR schedule.departure_airline_id = airline.id_airline
    #         WHERE
    #             (
    #                 schedule.valid_from <= '{start_date}' AND (schedule.valid_to IS NULL OR schedule.valid_to >= '{start_date}')
    #             )
    #         AND (
    #             (EXTRACT(DOW FROM '{start_date}'::date) = 0 AND (schedule.sunday_operation = TRUE OR schedule.sunday_operation IS NULL)) OR
    #             (EXTRACT(DOW FROM '{start_date}'::date) = 1 AND (schedule.monday_operation = TRUE OR schedule.monday_operation IS NULL)) OR
    #             (EXTRACT(DOW FROM '{start_date}'::date) = 2 AND (schedule.tuesday_operation = TRUE OR schedule.tuesday_operation IS NULL)) OR
    #             (EXTRACT(DOW FROM '{start_date}'::date) = 3 AND (schedule.wednesday_operation = TRUE OR schedule.wednesday_operation IS NULL)) OR
    #             (EXTRACT(DOW FROM '{start_date}'::date) = 4 AND (schedule.thursday_operation = TRUE OR schedule.thursday_operation IS NULL)) OR
    #             (EXTRACT(DOW FROM '{start_date}'::date) = 5 AND (schedule.friday_operation = TRUE OR schedule.friday_operation IS NULL)) OR
    #             (EXTRACT(DOW FROM '{start_date}'::date) = 6 AND (schedule.saturday_operation = TRUE OR schedule.saturday_operation IS NULL))
    #         )
            
    #     """
        
    
        #  AND (
        #         schedule.arrival_airline_id IN ({airline_id_tuple}) OR schedule.departure_airline_id IN ({airline_id_tuple})
        #     );

    # hour_wise_query = """
    #     WITH hour_series AS (
    #       SELECT
    #         generate_series(
    #           DATE_TRUNC('day', TIMESTAMP '2023-08-01'),
    #           DATE_TRUNC('day', TIMESTAMP '2023-08-01') + INTERVAL '1 day',
    #           INTERVAL '1 hour'
    #         ) AS hour_start,
    #         generate_series(
    #           DATE_TRUNC('day', TIMESTAMP '2023-08-01') + INTERVAL '1 hour',
    #           DATE_TRUNC('day', TIMESTAMP '2023-08-01') + INTERVAL '25 hour',
    #           INTERVAL '1 hour'
    #         ) AS hour_end
    #     )
    #     SELECT
    #         airlines.id_airline,
    #         airlines.airline_name,
    #         EXTRACT(HOUR FROM hour_series.hour_start) AS hour,
    #         COUNT(*) AS schedule_count
    #     FROM
    #       hour_series
    #     LEFT JOIN
    #       schedules
    #     ON
    #       TO_TIMESTAMP(LPAD(schedules.arrival_time, 4, '0'), 'HH24MI') >= hour_series.hour_start
    #       AND TO_TIMESTAMP(LPAD(schedules.departure_time, 4, '0'), 'HH24MI') <= hour_series.hour_end
    #     JOIN airlines ON airlines.id_airline = schedules.departure_airline_id
    #     GROUP BY
    #         airlines.id_airline,
    #         hour_series.hour_start
    #     ORDER BY
    #         airlines.id_airline,
    #         hour_series.hour_start;
    # """
    
    # Execute the SQL query
    with connection.cursor() as cursor:
        
        args = (date_query,join_condition, airline_id_query)
        if(start_date != end_date or day_wise):
            # for date range
            interval_type = "day"
            cursor.execute(day_wise_query % args)
        else:
            # for single date
            # if airline_id == []:
            interval_type = "hour"
            cursor.execute(build_hour_wise_query(start_date, filter_by, airline_id_tuple))
            # else:
            #     cursor.execute(build_hour_wise_query(start_date, filter_by) + airline_condition)
            
        # result = cursor.fetchall()
        total_data = {
            "airline_name": "Total",
            "date_range": []
        }
        columns = [desc[0] for desc in cursor.description]
        
        # checking if the date single or multiple
        if(start_date == end_date and day_wise == False):
            data = []
            for row in cursor.fetchall():
                data.append(dict(zip(columns, row)))
        else:
            result = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # calculate the total counts for the columns
        def add_total_count(data, curr_date):
            total_count = 0

            for curr_airline in data:
                curr_airline_date_range = curr_airline["date_range"]
                curr_date_count = list(filter(lambda date: date["date"] == curr_date, curr_airline_date_range))
                if curr_date_count and len(curr_date_count) > 0:
                    total_count = total_count + curr_date_count[0]['count']
                else:
                    total_count = total_count + 0

            return total_count
    
        hoursArray = []
        # if the it is just a single date then we need to append the data as hours 
        if(start_date == end_date and day_wise == False):
            finaldata = count_flights_by_hour(data),
            for hour in range(24):
                hoursArray.append(str(convert_to_time_format(hour)) + ' - ' + str(convert_to_time_format(hour + 1)))
                total_for_that_day = add_total_count(finaldata[0], str(convert_to_time_format(hour)) + ' - ' + str(convert_to_time_format(hour + 1)),)
                total_data['date_range'].append({
                    "date": str(convert_to_time_format(hour)) + ' - ' + str(convert_to_time_format(hour + 1)),
                    "count": total_for_that_day
                })
            finaldata[0].append(total_data)
        else:
            # calculate total for all the flights
            for curr_date in date_array:
                total_for_that_day = add_total_count(result, curr_date)
                total_data['date_range'].append({
                    "date": curr_date,
                    "count": total_for_that_day
                })
        
            result.append(total_data)
            
    
    # Initialize the result dictionary for all 24 hours with 0 employee count
    # result = {f"hr {i}-{i+1}": 0 for i in range(24)}

    # Loop through each hour and calculate the employee count
    # for hour in range(24):
    #     start_time = current_date.replace(hour=hour, minute=0, second=0, microsecond=0)
    #     end_time = start_time + timedelta(hours=1)

    #     flightsCount = Schedules.objects.filter(arrival_time__gte=start_time, arrival_time__lt=end_time).count()
    #     result[f"hr {hour}-{hour+1}"] = flightsCount
    
    response_data = {
            'success': True,
            'message': 'Data fetched successfully',
            'respayload': {
                'airlines_data': finaldata[0] if (start_date == end_date and day_wise == False) else result,
                'date_range':hoursArray if (start_date == end_date and day_wise == False) else date_array,
                "type": interval_type
            }
            # 'respayload': {
            #     'data':[] if finaldata is None else finaldata[0],
            #     'current_date': current_date,
            # }
        }
    return JsonResponse(response_data, safe=False)

def get_valid_date_range(current_date):
    # SQL query to fetch the valid date range for the current date
    sql_query = f"""
        SELECT MIN(valid_from), MAX(valid_to)
        FROM schedules
         WHERE
            (
                schedules.valid_from <= '{current_date}' AND (schedules.valid_to IS NULL OR schedules.valid_to >= '{current_date}')
            )
            OR
            (
                NOT EXISTS (SELECT 1 FROM schedules WHERE schedules.valid_from <= '{current_date}' AND (schedules.valid_to IS NULL OR schedules.valid_to >= '{current_date}'))
                AND
                schedules.valid_from = (SELECT MIN(valid_from) FROM schedules)
            )
    """

    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        row = cursor.fetchone()
        if row:
            valid_from, valid_to = row
            return valid_from, valid_to

    # If no schedules exist, return None for valid_from and valid_to
    return None, None

    #     # Read the Excel file into a pandas DataFrame
    #     df = pd.read_excel(file)

    #     # Convert the DataFrame to a list of dictionaries (to use orient='records')
    #     records = df.to_dict(orient='records')

    #     # Return the data as the API response
    #     return JsonResponse(records, safe=False)

    # return JsonResponse({'error': 'Invalid request'}, status=400)
     
    
def calculate_monthly_data(request, valid_from, valid_to):
    # Calculate the number of days in the date range
    date_range = (valid_to - valid_from).days + 1

    if date_range > 60:
        # If the date range is greater than 60 days, split it into monthly chunks
        num_months = date_range // 30
        remaining_days = date_range % 30

        valid_from_months = [valid_from + timedelta(days=30 * n) for n in range(num_months)]
        valid_to_months = [valid_from + timedelta(days=30 * (n + 1) - 1) for n in range(num_months)]

        # Adjust the last month if there are remaining days
        if remaining_days > 0:
            valid_from_months.append(valid_to - timedelta(days=remaining_days - 1))
            valid_to_months.append(valid_to)

    else:
        # Otherwise, use the entire date range as-is
        valid_from_months = [valid_from]
        valid_to_months = [valid_to]

    # Process the airlines_data dictionary and append it to the response_data
    response_data = {
        'success': True,
        'respayload': [],
        'message': 'OriginBasedairlines data is fetched successfully',
    }

    for i in range(len(valid_from_months)):
        valid_from_month = valid_from_months[i]
        valid_to_month = valid_to_months[i]

        sql_query = f"""
            SELECT
                origin.station_name AS origin_station_name,
                origin.station_code AS origin_station_code,
                airline.airline_name AS airline_name,
                schedule.valid_from AS valid_from,
                schedule.valid_to AS valid_to,
                schedule.monday_operation,
                schedule.tuesday_operation,
                schedule.wednesday_operation,
                schedule.thursday_operation,
                schedule.friday_operation,
                schedule.saturday_operation,
                schedule.sunday_operation
            FROM
                schedules AS schedule
            LEFT JOIN stations AS origin ON schedule.origin_station_id = origin.id_station
            LEFT JOIN airlines AS airline ON schedule.departure_airline_id = airline.id_airline
            WHERE schedule.valid_from BETWEEN '{valid_from_month}' AND '{valid_to_month}'
        """

        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            rows = cursor.fetchall()

        # Create a dictionary to store the monthly count for each airline
        airlines_data = defaultdict(lambda: {'origin_station_name': None, 'origin_station_code': None, 'monthly_count': 0})

        for row in rows:
            origin_station_name, origin_station_code, airline_name, valid_from, valid_to, *day_operations = row

            # Calculate the range of common dates within the valid date range based on the provided valid_from and valid_to
            common_dates_range = [date for date in (valid_from + timedelta(days=n) for n in range((valid_to - valid_from).days + 1))]

            # Update the origin station information
            airlines_data[airline_name]['origin_station_name'] = origin_station_name
            airlines_data[airline_name]['origin_station_code'] = origin_station_code

            for schedule_date in common_dates_range:
                day_of_week = schedule_date.weekday()
                day_operation_field = None

                if day_of_week == 0:
                    day_operation_field = 'monday_operation'
                elif day_of_week == 1:
                    day_operation_field = 'tuesday_operation'
                elif day_of_week == 2:
                    day_operation_field = 'wednesday_operation'
                elif day_of_week == 3:
                    day_operation_field = 'thursday_operation'
                elif day_of_week == 4:
                    day_operation_field = 'friday_operation'
                elif day_of_week == 5:
                    day_operation_field = 'saturday_operation'
                elif day_of_week == 6:
                    day_operation_field = 'sunday_operation'

                # Calculate the count based on the day operation field
                count = 1 if row[5 + day_of_week] else 0

                # Convert the schedule_date to a string representation
                date_str = schedule_date.strftime('%Y-%m-%d')

                # Update the overall count for the specific date and airline
                airlines_data[airline_name]['monthly_count'] += count

        # Append the monthly count to the response_data
        for airline_name, data in airlines_data.items():
            if data['monthly_count'] > 0:
                airline_data = {
                    'origin_station_name': data['origin_station_name'],
                    'origin_station_code': data['origin_station_code'],
                    'airlines_data': [
                        {
                            'airline_name': airline_name,
                            'monthly_count': data['monthly_count']
                        }
                    ],
                    'month_start_date': valid_from_month.strftime('%Y-%m-%d'),
                    'month_end_date': valid_to_month.strftime('%Y-%m-%d')
                }

                response_data['respayload'].append(airline_data)

    return JsonResponse(response_data)

def calculate_weekwise_data(request, valid_from, valid_to):
    # Calculate the number of days in the date range
    date_range = (valid_to - valid_from).days + 1

    if 30 < date_range <= 60:
        # If the date range is greater than 30 days and less than or equal to 60 days,
        # aggregate data weekly (7 days at a time)
        num_weeks = date_range // 7
        remaining_days = date_range % 7

        valid_from_weeks = [valid_from + timedelta(weeks=n * 7) for n in range(num_weeks)]
        valid_to_weeks = [valid_from_weeks[n] + timedelta(days=6) for n in range(num_weeks)]

        # Adjust the last week if there are remaining days
        if remaining_days > 0:
            valid_from_weeks.append(valid_to - timedelta(days=remaining_days - 1))
            valid_to_weeks.append(valid_to)

    else:
        # Otherwise, use the entire date range as-is
        valid_from_weeks = [valid_from]
        valid_to_weeks = [valid_to]

    # Initialize response_data
    response_data = {
        'success': True,
        'respayload': [],
        'message': 'OriginBasedairlines data is fetched successfully',
    }

    # Loop through the weekly date ranges and fetch the data for each week
    for i in range(len(valid_from_weeks)):
        # Fetch data for the current week
        valid_from_week = valid_from_weeks[i]
        valid_to_week = valid_to_weeks[i]

    # Loop through the weekly date ranges and fetch the data for each week
    for i in range(len(valid_from_weeks)):
        # Fetch data for the current week
        valid_from_week = valid_from_weeks[i]
        valid_to_week = valid_to_weeks[i]

        sql_query = f"""
            SELECT
                origin.station_name AS origin_station_name,
                origin.station_code AS origin_station_code,
                airline.airline_name AS airline_name,
                SUM(CAST(schedule.monday_operation AS INTEGER)) AS monday_operation,
                SUM(CAST(schedule.tuesday_operation AS INTEGER)) AS tuesday_operation,
                SUM(CAST(schedule.wednesday_operation AS INTEGER)) AS wednesday_operation,
                SUM(CAST(schedule.thursday_operation AS INTEGER)) AS thursday_operation,
                SUM(CAST(schedule.friday_operation AS INTEGER)) AS friday_operation,
                SUM(CAST(schedule.saturday_operation AS INTEGER)) AS saturday_operation,
                SUM(CAST(schedule.sunday_operation AS INTEGER)) AS sunday_operation
            FROM
                schedules AS schedule
            LEFT JOIN stations AS origin ON schedule.origin_station_id = origin.id_station
            LEFT JOIN airlines AS airline ON schedule.departure_airline_id = airline.id_airline
            WHERE schedule.valid_from BETWEEN '{valid_from_week}' AND '{valid_to_week}'
            GROUP BY origin.station_name, origin.station_code, airline.airline_name
        """

        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            rows = cursor.fetchall()

        # Create a dictionary to store the count for each date for each airline for the current week
        airlines_data = defaultdict(
            lambda: {'origin_station_name': None, 'origin_station_code': None, 'airlines_data': defaultdict(int)}
        )

        for row in rows:
            origin_station_name, origin_station_code, airline_name, *day_operations = row

            # Update the origin station information
            airlines_data[origin_station_code]['origin_station_name'] = origin_station_name
            airlines_data[origin_station_code]['origin_station_code'] = origin_station_code

            # Calculate the overall count for the current week for the specific airline
            weekly_count = sum(day_operations)

            airlines_data[origin_station_code]['airlines_data'][airline_name] += weekly_count

        # Process the airlines_data dictionary and append it to the response_data
        for origin_code, data in airlines_data.items():
            if not any(data['airlines_data']):
                continue  # Skip if there are no operations for the current station in the current week

            airline_data = {
                'origin_station_name': data['origin_station_name'],
                'origin_station_code': origin_code,
                'airlines_data': [
                    {
                        'airline_name': airline_name,
                        'weekly_count': count
                    }
                    for airline_name, count in data['airlines_data'].items()
                ],
                'week_start_date': valid_from_week.strftime('%Y-%m-%d'),
                'week_end_date': valid_to_week.strftime('%Y-%m-%d')
            }

            response_data['respayload'].append(airline_data)

    return JsonResponse(response_data)

def calculate_datewise_data(request, current_date):
   # Get the current date
    current_date = timezone.datetime.now().date()

    # Check if valid_from and valid_to parameters are present in the request
    valid_from = request.GET.get('valid_from', None)
    valid_to = request.GET.get('valid_to', None)

    if not valid_from or not valid_to:
        # If valid_from or valid_to is not provided, get the valid date range for the current date
        valid_from, valid_to = get_valid_date_range(current_date)

    # SQL query to fetch the data for the common dates and their counts
    sql_query = f"""
        SELECT
            origin.station_name AS origin_station_name,
            origin.station_code AS origin_station_code,
            airline.airline_name AS airline_name,
            schedule.valid_from AS valid_from,
            schedule.valid_to AS valid_to,
            schedule.monday_operation,
            schedule.tuesday_operation,
            schedule.wednesday_operation,
            schedule.thursday_operation,
            schedule.friday_operation,
            schedule.saturday_operation,
            schedule.sunday_operation
        FROM
            schedules AS schedule
        LEFT JOIN stations AS origin ON schedule.origin_station_id = origin.id_station
        LEFT JOIN airlines AS airline ON schedule.departure_airline_id = airline.id_airline
        WHERE schedule.valid_from BETWEEN '{valid_from}' AND '{valid_to}'
    """

    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        rows = cursor.fetchall()

    # Create a dictionary to store the count for each date for each airline
    airlines_data = defaultdict(lambda: {'origin_station_name': None, 'origin_station_code': None, 'airlines_data': defaultdict(lambda: {'dates': defaultdict(int)})})

    for row in rows:
        origin_station_name, origin_station_code, airline_name, valid_from, valid_to, monday_operation, tuesday_operation, wednesday_operation, thursday_operation, friday_operation, saturday_operation, sunday_operation = row

        # Calculate the range of common dates within the valid date range based on the provided valid_from and valid_to
        common_dates_range = [date for date in (valid_from + timedelta(days=n) for n in range((valid_to - valid_from).days + 1))]

        # Update the origin station information
        airlines_data[origin_station_code]['origin_station_name'] = origin_station_name
        airlines_data[origin_station_code]['origin_station_code'] = origin_station_code

        for schedule_date in common_dates_range:
            day_of_week = schedule_date.weekday()
            day_operation_field = None

            if day_of_week == 0:
                day_operation_field = 'monday_operation'
            elif day_of_week == 1:
                day_operation_field = 'tuesday_operation'
            elif day_of_week == 2:
                day_operation_field = 'wednesday_operation'
            elif day_of_week == 3:
                day_operation_field = 'thursday_operation'
            elif day_of_week == 4:
                day_operation_field = 'friday_operation'
            elif day_of_week == 5:
                day_operation_field = 'saturday_operation'
            elif day_of_week == 6:
                day_operation_field = 'sunday_operation'

            # Calculate the count based on the day operation field
            count = 1 if row[5 + day_of_week] else 0

            # Convert the schedule_date to a string representation
            date_str = schedule_date.strftime('%Y-%m-%d')

            # Update the overall count for the specific date and airline
            airlines_data[origin_station_code]['airlines_data'][airline_name]['dates'][date_str] += count

    # Process the airlines_data dictionary and create the JSON response
    response_data = {
        'success': True,
        'respayload': [],
        'message': 'OriginBasedairlines data is fetched successfully',
    }

    for origin_code, data in airlines_data.items():
        if not any(data['airlines_data']):
            continue  # Skip if there are no common dates for the current station

        airline_data = {
            'origin_station_name': data['origin_station_name'],
            'origin_station_code': origin_code,
            'airlines_data': []
        }

        for airline_name, dates in data['airlines_data'].items():
            if not any(dates['dates']):
                continue  # Skip if there are no common dates for the current airline

            airline_dates = {
                'airline_name': airline_name,
                'dates': [{'date': date_str, 'count': count} for date_str, count in dates['dates'].items()]
            }
            airline_data['airlines_data'].append(airline_dates)

        response_data['respayload'].append(airline_data)

    return JsonResponse(response_data)


def OriginBasedAirlineswise(request):

    valid_from = request.GET.get('valid_from', None)
    valid_to = request.GET.get('valid_to', None)

    valid_from_date = datetime.strptime(valid_from, '%Y-%m-%d').date() if valid_from else None
    valid_to_date = datetime.strptime(valid_to, '%Y-%m-%d').date() if valid_to else None

    data_type = ""
    
    week_based_sql_query = """
        WITH ScheduleDates AS (
            SELECT
                origin_station_id,
                origin_station.station_name,
                arrival_airline_id,
                origin_airline.airline_name,
                valid_from::date AS date_from,
                valid_to::date AS date_to
            FROM
                schedules
            LEFT JOIN stations AS origin_station ON schedules.origin_station_id = origin_station.id_station
            LEFT JOIN airlines AS origin_airline ON schedules.departure_airline_id = origin_airline.id_airline
            WHERE
                valid_from::date BETWEEN %s AND %s
                AND valid_to::date BETWEEN %s AND %s
        )
        , ExpandedDates AS (
            SELECT
                origin_station_id,
                station_name,
                arrival_airline_id,
                airline_name,
                generate_series(date_from, date_to, '1 week'::interval) AS week_start
            FROM
                ScheduleDates
        )
        , WeekCounts AS (
            SELECT
                origin_station_id,
                station_name,
                arrival_airline_id,
                airline_name,
                week_start,
                COUNT(*) AS count
            FROM
                ExpandedDates
            GROUP BY
                origin_station_id,
                station_name,
                arrival_airline_id,
                airline_name,
                week_start
        )
        , IntermediateResult AS (
            SELECT
                origin_station_id,
                station_name,
                arrival_airline_id,
                airline_name,
                week_start,
                to_char(week_start, 'yyyy-mm-dd') || ' / ' || to_char((week_start + '6 days'::interval), 'yyyy-mm-dd') AS date_range,
                count
            FROM
                WeekCounts
        )
        SELECT
            origin_station_id,
            station_name,
            json_agg(airline_info) AS airlines_data
        FROM (
            SELECT
                origin_station_id,
                station_name,
                arrival_airline_id,
                airline_name,
                json_build_object(
                    'airline_id', arrival_airline_id,
                    'airline_name', airline_name,
                    'dates', json_agg(date_info)
                ) AS airline_info
            FROM (
                SELECT
                    origin_station_id,
                    station_name,
                    arrival_airline_id,
                    airline_name,
                    week_start,
                    json_build_object(
                        'date', date_range,
                        'count', count
                    ) AS date_info
                FROM
                    IntermediateResult
            ) AS date_info_subquery
            GROUP BY
                origin_station_id,
                station_name,
                arrival_airline_id,
                airline_name
        ) AS schedule_type_info_subquery
        GROUP BY
            origin_station_id,
            station_name;
    """

    hour_wise_query = """
        CREATE TEMPORARY TABLE IF NOT EXISTS TempHourlyScheduleCounts (
            origin_station_id TEXT,
            arrival_airline_id TEXT,
            station_name TEXT,
            station_code TEXT,
            airline_name TEXT,
            airline_code TEXT,
            hour_interval TEXT,
            schedule_count INT
        );

        INSERT INTO TempHourlyScheduleCounts
        SELECT
            origin_station_id,
            arrival_airline_id,
            origin_station.station_name AS station_name,
            origin_station.station_code AS station_code,
            origin_airline.airline_name AS airline_name,
            origin_airline.airline_code AS airline_code,
            CASE
                WHEN departure_time >= '0000' AND departure_time <= '0059' THEN '00:00 - 01:00'
                WHEN departure_time >= '0100' AND departure_time <= '0159' THEN '01:00 - 02:00'
                WHEN departure_time >= '0200' AND departure_time <= '0259' THEN '02:00 - 03:00'
                WHEN departure_time >= '0300' AND departure_time <= '0359' THEN '03:00 - 04:00'
                WHEN departure_time >= '0400' AND departure_time <= '0459' THEN '04:00 - 05:00'
                WHEN departure_time >= '0500' AND departure_time <= '0559' THEN '05:00 - 06:00'
                WHEN departure_time >= '0600' AND departure_time <= '0659' THEN '06:00 - 07:00'
                WHEN departure_time >= '0700' AND departure_time <= '0759' THEN '07:00 - 08:00'
                WHEN departure_time >= '0800' AND departure_time <= '0859' THEN '08:00 - 09:00'
                WHEN departure_time >= '0900' AND departure_time <= '0959' THEN '09:00 - 10:00'
                WHEN departure_time >= '1000' AND departure_time <= '1059' THEN '10:00 - 11:00'
                WHEN departure_time >= '1100' AND departure_time <= '1159' THEN '11:00 - 12:00'
                WHEN departure_time >= '1200' AND departure_time <= '1259' THEN '12:00 - 13:00'
                WHEN departure_time >= '1300' AND departure_time <= '1359' THEN '13:00 - 14:00'
                WHEN departure_time >= '1400' AND departure_time <= '1459' THEN '14:00 - 15:00'
                WHEN departure_time >= '1500' AND departure_time <= '1559' THEN '15:00 - 16:00'
                WHEN departure_time >= '1600' AND departure_time <= '1659' THEN '16:00 - 17:00'
                WHEN departure_time >= '1700' AND departure_time <= '1759' THEN '17:00 - 18:00'
                WHEN departure_time >= '1800' AND departure_time <= '1859' THEN '18:00 - 19:00'
                WHEN departure_time >= '1900' AND departure_time <= '1959' THEN '19:00 - 20:00'
                WHEN departure_time >= '2000' AND departure_time <= '2059' THEN '20:00 - 21:00'
                WHEN departure_time >= '2100' AND departure_time <= '2159' THEN '21:00 - 22:00'
                WHEN departure_time >= '2200' AND departure_time <= '2259' THEN '22:00 - 23:00'
                WHEN departure_time >= '2300' AND departure_time <= '2359' THEN '23:00 - 24:00'
                ELSE 'Unknown'
            END AS hour_interval,
            COUNT(*) AS schedule_count
        FROM schedules
        JOIN stations origin_station ON origin_station_id = id_station
        JOIN airlines origin_airline ON arrival_airline_id = id_airline
        WHERE valid_from <= %s::DATE AND valid_to >= %s::DATE
        GROUP BY
            origin_station_id,
            arrival_airline_id,
            station_name,
            station_code,
            airline_name,
            airline_code,
            hour_interval;

        SELECT
            origin_station_id,
            station_name,
            json_agg(airline_info) AS airlines_data
        FROM (
            SELECT
                origin_station_id,
                station_name,
                arrival_airline_id,
                airline_name,
                json_build_object(
                    'airline_id', arrival_airline_id,
                    'airline_name', airline_name,
                    'dates', json_agg(date_info)
                ) AS airline_info
                FROM (
                    SELECT
                        origin_station_id,
                        station_name,
                        arrival_airline_id,
                        airline_name,
                        json_build_object(
                            'date', hour_interval,
                            'count', schedule_count
                        ) AS date_info
                    FROM
                        TempHourlyScheduleCounts
                ) AS date_info_subquery
                GROUP BY
                    origin_station_id,
                    station_name,
                    arrival_airline_id,
                    airline_name
        ) AS schedule_type_info_subquery
        GROUP BY
            origin_station_id,
            station_name
        ORDER BY
            origin_station_id,
            station_name
    """
    
    month_wise_query = """
        CREATE TEMPORARY TABLE IF NOT EXISTS TempMonthlyScheduleCounts (
            origin_station_id TEXT,
            arrival_airline_id TEXT,
            station_name TEXT,
            station_code TEXT,
            airline_name TEXT,
            airline_code TEXT,
            month TEXT,
            schedule_count INT
        );

        INSERT INTO TempMonthlyScheduleCounts
        SELECT
            origin_station_id,
            arrival_airline_id,
            origin_station.station_name AS station_name,
            origin_station.station_code AS station_code,
            origin_airline.airline_name AS airline_name,
            origin_airline.airline_code AS airline_code,
            to_char(date_trunc('month', valid_from), 'Mon') AS month,
            COUNT(*) AS schedule_count
        FROM schedules
        JOIN stations origin_station ON origin_station_id = id_station
        JOIN airlines origin_airline ON arrival_airline_id = id_airline
        WHERE 
            (valid_from <= %s::DATE AND valid_to >= %s::DATE) OR
            (valid_from <= %s::DATE AND valid_to >= %s::DATE)
        GROUP BY
            origin_station_id,
            arrival_airline_id,
            station_name,
            station_code,
            airline_name,
            airline_code,
            month;

        SELECT
            origin_station_id,
            station_name,
            json_agg(airline_info) AS airlines_data
        FROM (
            SELECT
                origin_station_id,
                station_name,
                arrival_airline_id,
                airline_name,
                json_build_object(
                    'airline_id', arrival_airline_id,
                    'airline_name', airline_name,
                    'dates', json_agg(date_info)
                ) AS airline_info
                FROM (
                    SELECT
                        origin_station_id,
                        station_name,
                        arrival_airline_id,
                        airline_name,
                        json_build_object(
                            'date', month,
                            'count', schedule_count
                        ) AS date_info
                    FROM
                        TempMonthlyScheduleCounts
                ) AS date_info_subquery
                GROUP BY
                    origin_station_id,
                    station_name,
                    arrival_airline_id,
                    airline_name
        ) AS schedule_type_info_subquery
        GROUP BY
            origin_station_id,
            station_name
        ORDER BY
            origin_station_id,
            station_name;
    """
    
    day_wise_query = """
        CREATE TEMPORARY TABLE IF NOT EXISTS TempDailyScheduleCounts (
                origin_station_id INT,
                arrival_airline_id INT,
                station_name TEXT,
                station_code TEXT,
                airline_name TEXT,
                airline_code TEXT,
                date DATE,
                schedule_count INT
            );

            INSERT INTO TempDailyScheduleCounts
            SELECT
                origin_station_id,
                arrival_airline_id,
                origin_station.station_name AS station_name,
                origin_station.station_code AS station_code,
                origin_airline.airline_name AS airline_name,
                origin_airline.airline_code AS airline_code,
                generate_series(%s, %s, interval '1 day')::date,
                COUNT(*) AS schedule_count
            FROM schedules
            JOIN stations origin_station ON origin_station_id = id_station
            JOIN airlines origin_airline ON arrival_airline_id = id_airline
            WHERE valid_from <= %s AND valid_to >= %s
            GROUP BY
                origin_station_id,
                arrival_airline_id,
                station_name,
                station_code,
                airline_name,
                airline_code,
                generate_series(%s, %s, interval '1 day')::date;

            
            SELECT
            origin_station_id,
            station_name,
            json_agg(airline_info) AS airlines_data
            FROM (
                 SELECT
                    origin_station_id,
                    arrival_airline_id,
                    station_name,
                    airline_name,
                    json_build_object(
                        'airline_id', arrival_airline_id,
                        'airline_name', airline_name,
                        'dates', json_agg(dates)
                    ) AS airline_info
                    FROM (
                        SELECT
                            all_date_combinations.origin_station_id,
                            all_date_combinations.arrival_airline_id,
                            all_date_combinations.station_name,
                            all_date_combinations.station_code,
                            all_date_combinations.airline_name,
                            all_date_combinations.airline_code,
                            json_build_object(
                                'date', all_date_combinations.date::text,
                                'count', schedule_count
                            ) AS dates
                        FROM (
                            SELECT origin_station_id, arrival_airline_id, origin_station.station_name, origin_station.station_code, origin_airline.airline_name, origin_airline.airline_code, generate_series(%s::date, %s::date, interval '1 day') AS date
                            FROM schedules
                            JOIN stations origin_station ON origin_station_id = id_station
                            JOIN airlines origin_airline ON arrival_airline_id = id_airline
                            WHERE valid_from <= %s AND valid_to >= %s
                            GROUP BY 
                                origin_station_id, 
                                arrival_airline_id, 
                                station_name,
                                station_code,
                                airline_name,
                                airline_code,
                                valid_from, 
                                valid_to
                        ) AS all_date_combinations
                        LEFT JOIN TempDailyScheduleCounts ON all_date_combinations.origin_station_id = TempDailyScheduleCounts.origin_station_id
                                                AND all_date_combinations.arrival_airline_id = TempDailyScheduleCounts.arrival_airline_id
                                                AND to_char(all_date_combinations.date, 'YYYY-MM-DD') = to_char(TempDailyScheduleCounts.date, 'YYYY-MM-DD')
                    ) AS date_info_subquery
                    GROUP BY
                        origin_station_id,
                        station_name,
                        arrival_airline_id,
                        airline_name
            ) AS schedule_type_info_subquery
            GROUP BY
                origin_station_id,
                station_name
            ORDER BY
                origin_station_id,
                station_name
    """
    
    with connection.cursor() as cursor:
        result = []
        date_intervals = []
        filtered_data = []
        if valid_from_date and valid_to_date:
            date_difference = (valid_to_date - valid_from_date).days

            if valid_from == valid_to:
                data_type = "hour"
                date_intervals = ['00:00 - 01:00', '01:00 - 02:00', '02:00 - 03:00', '03:00 - 04:00', '04:00 - 05:00', '05:00 - 06:00', '06:00 - 07:00', '07:00 - 08:00', '08:00 - 09:00', '09:00 - 10:00', '10:00 - 11:00', '11:00 - 12:00', '12:00 - 13:00', '13:00 - 14:00', '14:00 - 15:00', '15:00 - 16:00', '16:00 - 17:00', '17:00 - 18:00', '18:00 - 19:00', '19:00 - 20:00', '20:00 - 21:00', '21:00 - 22:00', '22:00 - 23:00', '23:00 - 24:00']
                cursor.execute(hour_wise_query, [valid_from, valid_to])
                columns = [desc[0] for desc in cursor.description]
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            elif date_difference < 30:
                data_type = "day"
                date_intervals = calculate_date_between_range(valid_from, valid_to)
                cursor.execute(day_wise_query, [valid_from, valid_to, valid_to, valid_from, valid_from, valid_to, valid_from, valid_to, valid_to, valid_from])
                columns = [desc[0] for desc in cursor.description]
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            elif 30 < date_difference <= 60:
                data_type = "week"
                date_intervals = generate_week_intervals(valid_from, valid_to)
                cursor.execute(week_based_sql_query, [valid_from, valid_from, valid_to, valid_to])
                columns = [desc[0] for desc in cursor.description]
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            elif date_difference > 60:
                data_type = "month"
                date_intervals = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                cursor.execute(month_wise_query, [valid_from, valid_from, valid_to, valid_to])
                columns = [desc[0] for desc in cursor.description]
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]

        for curr_origin in result:
            curr_data = {
                "origin_station_id": curr_origin["origin_station_id"],
                "station_name": curr_origin["station_name"],
                "airlines_data": []
            }
            
            for airline in curr_origin["airlines_data"]:
                curr_airline_data = {
                    "airline_id": airline["airline_id"],
                    "airline_name": airline["airline_name"],
                    "dates": []
                }
            
                for curr_date in date_intervals:
                    data_avail = next(
                        (obj for obj in airline["dates"] if obj["date"] == curr_date),
                        None
                    )
                    if data_avail:
                        curr_airline_data["dates"].append(data_avail)
                    else:
                        curr_airline_data["dates"].append({
                            "date": curr_date,
                            "count": 0
                        })
            
                curr_data['airlines_data'].append(curr_airline_data)
            
            filtered_data.append(curr_data)
            

        response_data = {
            'success': True,
            'respayload': {
                "data": filtered_data,
                "date_intervals": date_intervals,
                "type": data_type
            },
            'message': 'OriginBasedairlines data is fetched successfully',
        }

    return JsonResponse(response_data)


def DestinationBasedAirlineswise(request):

    valid_from = request.GET.get('valid_from', None)
    valid_to = request.GET.get('valid_to', None)

    valid_from_date = datetime.strptime(valid_from, '%Y-%m-%d').date() if valid_from else None
    valid_to_date = datetime.strptime(valid_to, '%Y-%m-%d').date() if valid_to else None

    data_type = ""
    
    week_based_sql_query = """
        WITH ScheduleDates AS (
            SELECT
                destination_station_id,
                destination_station.station_name,
                departure_airline_id,
                destination_airline.airline_name,
                valid_from::date AS date_from,
                valid_to::date AS date_to
            FROM
                schedules
            LEFT JOIN stations AS destination_station ON schedules.destination_station_id = destination_station.id_station
            LEFT JOIN airlines AS destination_airline ON schedules.departure_airline_id = destination_airline.id_airline
            WHERE
                valid_from::date BETWEEN %s AND %s
                AND valid_to::date BETWEEN %s AND %s
        )
        , ExpandedDates AS (
            SELECT
                destination_station_id,
                station_name,
                departure_airline_id,
                airline_name,
                generate_series(date_from, date_to, '1 week'::interval) AS week_start
            FROM
                ScheduleDates
        )
        , WeekCounts AS (
            SELECT
                destination_station_id,
                station_name,
                departure_airline_id,
                airline_name,
                week_start,
                COUNT(*) AS count
            FROM
                ExpandedDates
            GROUP BY
                destination_station_id,
                station_name,
                departure_airline_id,
                airline_name,
                week_start
        )
        , IntermediateResult AS (
            SELECT
                destination_station_id,
                station_name,
                departure_airline_id,
                airline_name,
                week_start,
                to_char(week_start, 'yyyy-mm-dd') || ' / ' || to_char((week_start + '6 days'::interval), 'yyyy-mm-dd') AS date_range,
                count
            FROM
                WeekCounts
        )
        SELECT
            destination_station_id,
            station_name,
            json_agg(airline_info) AS airlines_data
        FROM (
            SELECT
                destination_station_id,
                station_name,
                departure_airline_id,
                airline_name,
                json_build_object(
                    'airline_id', departure_airline_id,
                    'airline_name', airline_name,
                    'dates', json_agg(date_info)
                ) AS airline_info
            FROM (
                SELECT
                    destination_station_id,
                    station_name,
                    departure_airline_id,
                    airline_name,
                    week_start,
                    json_build_object(
                        'date', date_range,
                        'count', count
                    ) AS date_info
                FROM
                    IntermediateResult
            ) AS date_info_subquery
            GROUP BY
                destination_station_id,
                station_name,
                departure_airline_id,
                airline_name
        ) AS schedule_type_info_subquery
        GROUP BY
            destination_station_id,
            station_name;
    """

    hour_wise_query = """
        CREATE TEMPORARY TABLE IF NOT EXISTS TempHourlyScheduleCounts (
            destination_station_id TEXT,
            departure_airline_id TEXT,
            station_name TEXT,
            station_code TEXT,
            airline_name TEXT,
            airline_code TEXT,
            hour_interval TEXT,
            schedule_count INT
        );

        INSERT INTO TempHourlyScheduleCounts
        SELECT
            destination_station_id,
            departure_airline_id,
            destination_station.station_name AS station_name,
            destination_station.station_code AS station_code,
            destination_airline.airline_name AS airline_name,
            destination_airline.airline_code AS airline_code,
            CASE
                WHEN departure_time >= '0000' AND departure_time <= '0059' THEN '00:00 - 01:00'
                WHEN departure_time >= '0100' AND departure_time <= '0159' THEN '01:00 - 02:00'
                WHEN departure_time >= '0200' AND departure_time <= '0259' THEN '02:00 - 03:00'
                WHEN departure_time >= '0300' AND departure_time <= '0359' THEN '03:00 - 04:00'
                WHEN departure_time >= '0400' AND departure_time <= '0459' THEN '04:00 - 05:00'
                WHEN departure_time >= '0500' AND departure_time <= '0559' THEN '05:00 - 06:00'
                WHEN departure_time >= '0600' AND departure_time <= '0659' THEN '06:00 - 07:00'
                WHEN departure_time >= '0700' AND departure_time <= '0759' THEN '07:00 - 08:00'
                WHEN departure_time >= '0800' AND departure_time <= '0859' THEN '08:00 - 09:00'
                WHEN departure_time >= '0900' AND departure_time <= '0959' THEN '09:00 - 10:00'
                WHEN departure_time >= '1000' AND departure_time <= '1059' THEN '10:00 - 11:00'
                WHEN departure_time >= '1100' AND departure_time <= '1159' THEN '11:00 - 12:00'
                WHEN departure_time >= '1200' AND departure_time <= '1259' THEN '12:00 - 13:00'
                WHEN departure_time >= '1300' AND departure_time <= '1359' THEN '13:00 - 14:00'
                WHEN departure_time >= '1400' AND departure_time <= '1459' THEN '14:00 - 15:00'
                WHEN departure_time >= '1500' AND departure_time <= '1559' THEN '15:00 - 16:00'
                WHEN departure_time >= '1600' AND departure_time <= '1659' THEN '16:00 - 17:00'
                WHEN departure_time >= '1700' AND departure_time <= '1759' THEN '17:00 - 18:00'
                WHEN departure_time >= '1800' AND departure_time <= '1859' THEN '18:00 - 19:00'
                WHEN departure_time >= '1900' AND departure_time <= '1959' THEN '19:00 - 20:00'
                WHEN departure_time >= '2000' AND departure_time <= '2059' THEN '20:00 - 21:00'
                WHEN departure_time >= '2100' AND departure_time <= '2159' THEN '21:00 - 22:00'
                WHEN departure_time >= '2200' AND departure_time <= '2259' THEN '22:00 - 23:00'
                WHEN departure_time >= '2300' AND departure_time <= '2359' THEN '23:00 - 24:00'
                ELSE 'Unknown'
            END AS hour_interval,
            COUNT(*) AS schedule_count
        FROM schedules
        JOIN stations destination_station ON destination_station_id = id_station
        JOIN airlines destination_airline ON departure_airline_id = id_airline
        WHERE valid_from <= %s::DATE AND valid_to >= %s::DATE
        GROUP BY
            destination_station_id,
            departure_airline_id,
            station_name,
            station_code,
            airline_name,
            airline_code,
            hour_interval;

        SELECT
            destination_station_id,
            station_name,
            json_agg(airline_info) AS airlines_data
        FROM (
            SELECT
                destination_station_id,
                station_name,
                departure_airline_id,
                airline_name,
                json_build_object(
                    'airline_id', departure_airline_id,
                    'airline_name', airline_name,
                    'dates', json_agg(date_info)
                ) AS airline_info
                FROM (
                    SELECT
                        destination_station_id,
                        station_name,
                        departure_airline_id,
                        airline_name,
                        json_build_object(
                            'date', hour_interval,
                            'count', schedule_count
                        ) AS date_info
                    FROM
                        TempHourlyScheduleCounts
                ) AS date_info_subquery
                GROUP BY
                    destination_station_id,
                    station_name,
                    departure_airline_id,
                    airline_name
        ) AS schedule_type_info_subquery
        GROUP BY
            destination_station_id,
            station_name
        ORDER BY
            destination_station_id,
            station_name
    """
    
    month_wise_query = """
        CREATE TEMPORARY TABLE IF NOT EXISTS TempMonthlyScheduleCounts (
            destination_station_id TEXT,
            departure_airline_id TEXT,
            station_name TEXT,
            station_code TEXT,
            airline_name TEXT,
            airline_code TEXT,
            month TEXT,
            schedule_count INT
        );

        INSERT INTO TempMonthlyScheduleCounts
        SELECT
            destination_station_id,
            departure_airline_id,
            destination_station.station_name AS station_name,
            destination_station.station_code AS station_code,
            destination_airline.airline_name AS airline_name,
            destination_airline.airline_code AS airline_code,
            to_char(date_trunc('month', valid_from), 'Mon') AS month,
            COUNT(*) AS schedule_count
        FROM schedules
        JOIN stations destination_station ON destination_station_id = id_station
        JOIN airlines destination_airline ON departure_airline_id = id_airline
        WHERE 
            (valid_from <= %s::DATE AND valid_to >= %s::DATE) OR
            (valid_from <= %s::DATE AND valid_to >= %s::DATE)
        GROUP BY
            destination_station_id,
            departure_airline_id,
            station_name,
            station_code,
            airline_name,
            airline_code,
            month;

        SELECT
            destination_station_id,
            station_name,
            json_agg(airline_info) AS airlines_data
        FROM (
            SELECT
                destination_station_id,
                station_name,
                departure_airline_id,
                airline_name,
                json_build_object(
                    'airline_id', departure_airline_id,
                    'airline_name', airline_name,
                    'dates', json_agg(date_info)
                ) AS airline_info
                FROM (
                    SELECT
                        destination_station_id,
                        station_name,
                        departure_airline_id,
                        airline_name,
                        json_build_object(
                            'date', month,
                            'count', schedule_count
                        ) AS date_info
                    FROM
                        TempMonthlyScheduleCounts
                ) AS date_info_subquery
                GROUP BY
                    destination_station_id,
                    station_name,
                    departure_airline_id,
                    airline_name
        ) AS schedule_type_info_subquery
        GROUP BY
            destination_station_id,
            station_name
        ORDER BY
            destination_station_id,
            station_name;
    """
    
    day_wise_query = """
        CREATE TEMPORARY TABLE IF NOT EXISTS TempDailyScheduleCounts (
                destination_station_id INT,
                departure_airline_id INT,
                station_name TEXT,
                station_code TEXT,
                airline_name TEXT,
                airline_code TEXT,
                date DATE,
                schedule_count INT
            );

            INSERT INTO TempDailyScheduleCounts
            SELECT
                destination_station_id,
                departure_airline_id,
                destination_station.station_name AS station_name,
                destination_station.station_code AS station_code,
                destination_airline.airline_name AS airline_name,
                destination_airline.airline_code AS airline_code,
                generate_series(%s, %s, interval '1 day')::date,
                COUNT(*) AS schedule_count
            FROM schedules
            JOIN stations destination_station ON destination_station_id = id_station
            JOIN airlines destination_airline ON departure_airline_id = id_airline
            WHERE valid_from <= %s AND valid_to >= %s
            GROUP BY
                destination_station_id,
                departure_airline_id,
                station_name,
                station_code,
                airline_name,
                airline_code,
                generate_series(%s, %s, interval '1 day')::date;

            
            SELECT
            destination_station_id,
            station_name,
            json_agg(airline_info) AS airlines_data
            FROM (
                 SELECT
                    destination_station_id,
                    departure_airline_id,
                    station_name,
                    airline_name,
                    json_build_object(
                        'airline_id', departure_airline_id,
                        'airline_name', airline_name,
                        'dates', json_agg(dates)
                    ) AS airline_info
                    FROM (
                        SELECT
                            all_date_combinations.destination_station_id,
                            all_date_combinations.departure_airline_id,
                            all_date_combinations.station_name,
                            all_date_combinations.station_code,
                            all_date_combinations.airline_name,
                            all_date_combinations.airline_code,
                            json_build_object(
                                'date', all_date_combinations.date::text,
                                'count', schedule_count
                            ) AS dates
                        FROM (
                            SELECT destination_station_id, departure_airline_id, destination_station.station_name, destination_station.station_code, destination_airline.airline_name, destination_airline.airline_code, generate_series(%s::date, %s::date, interval '1 day') AS date
                            FROM schedules
                            JOIN stations destination_station ON destination_station_id = id_station
                            JOIN airlines destination_airline ON departure_airline_id = id_airline
                            WHERE valid_from <= %s AND valid_to >= %s
                            GROUP BY 
                                destination_station_id, 
                                departure_airline_id, 
                                station_name,
                                station_code,
                                airline_name,
                                airline_code,
                                valid_from, 
                                valid_to
                        ) AS all_date_combinations
                        LEFT JOIN TempDailyScheduleCounts ON all_date_combinations.destination_station_id = TempDailyScheduleCounts.destination_station_id
                                                AND all_date_combinations.departure_airline_id = TempDailyScheduleCounts.departure_airline_id
                                                AND to_char(all_date_combinations.date, 'YYYY-MM-DD') = to_char(TempDailyScheduleCounts.date, 'YYYY-MM-DD')
                    ) AS date_info_subquery
                    GROUP BY
                        destination_station_id,
                        station_name,
                        departure_airline_id,
                        airline_name
            ) AS schedule_type_info_subquery
            GROUP BY
                destination_station_id,
                station_name
            ORDER BY
                destination_station_id,
                station_name
    """
    
    with connection.cursor() as cursor:
        result = []
        date_intervals = []
        filtered_data = []
        if valid_from_date and valid_to_date:
            date_difference = (valid_to_date - valid_from_date).days

            if valid_from == valid_to:
                data_type = "hour"
                date_intervals = ['00:00 - 01:00', '01:00 - 02:00', '02:00 - 03:00', '03:00 - 04:00', '04:00 - 05:00', '05:00 - 06:00', '06:00 - 07:00', '07:00 - 08:00', '08:00 - 09:00', '09:00 - 10:00', '10:00 - 11:00', '11:00 - 12:00', '12:00 - 13:00', '13:00 - 14:00', '14:00 - 15:00', '15:00 - 16:00', '16:00 - 17:00', '17:00 - 18:00', '18:00 - 19:00', '19:00 - 20:00', '20:00 - 21:00', '21:00 - 22:00', '22:00 - 23:00', '23:00 - 24:00']
                cursor.execute(hour_wise_query, [valid_from, valid_to])
                columns = [desc[0] for desc in cursor.description]
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            elif date_difference < 30:
                data_type = "day"
                date_intervals = calculate_date_between_range(valid_from, valid_to)
                cursor.execute(day_wise_query, [valid_from, valid_to, valid_to, valid_from, valid_from, valid_to, valid_from, valid_to, valid_to, valid_from])
                columns = [desc[0] for desc in cursor.description]
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            elif 30 < date_difference <= 60:
                data_type = "week"
                date_intervals = generate_week_intervals(valid_from, valid_to)
                cursor.execute(week_based_sql_query, [valid_from, valid_from, valid_to, valid_to])
                columns = [desc[0] for desc in cursor.description]
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            elif date_difference > 60:
                data_type = "month"
                date_intervals = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                cursor.execute(month_wise_query, [valid_from, valid_from, valid_to, valid_to])
                columns = [desc[0] for desc in cursor.description]
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]

        for curr_destination in result:
            curr_data = {
                "destination_station_id": curr_destination["destination_station_id"],
                "station_name": curr_destination["station_name"],
                "airlines_data": []
            }
            
            for airline in curr_destination["airlines_data"]:
                curr_airline_data = {
                    "airline_id": airline["airline_id"],
                    "airline_name": airline["airline_name"],
                    "dates": []
                }
            
                for curr_date in date_intervals:
                    data_avail = next(
                        (obj for obj in airline["dates"] if obj["date"] == curr_date),
                        None
                    )
                    if data_avail:
                        curr_airline_data["dates"].append(data_avail)
                    else:
                        curr_airline_data["dates"].append({
                            "date": curr_date,
                            "count": 0
                        })
            
                curr_data['airlines_data'].append(curr_airline_data)
            
            filtered_data.append(curr_data)
            

        response_data = {
            'success': True,
            'respayload': {
                "data": filtered_data,
                "date_intervals": date_intervals,
                "type": data_type
            },
            'message': 'Destination Based Airlines data is fetched successfully',
        }

    return JsonResponse(response_data)

def aircraftBasedAirlinesSeatCount(request):
    current_date = timezone.now().date()

    valid_from_str = request.GET.get('valid_from')
    valid_to_str = request.GET.get('valid_to')

    if valid_from_str:
        valid_from = datetime.strptime(valid_from_str, '%Y-%m-%d').date()
    else:
        valid_from, _ = get_valid_date_range(current_date)  # Unpack the tuple, but ignore valid_to

    if valid_to_str:
        valid_to = datetime.strptime(valid_to_str, '%Y-%m-%d').date()
    else:
         valid_to = valid_from + timezone.timedelta(days=9)

    # Construct the SQL query
    query = """
        SELECT
            aircraft.aircraft_name,
            airline.airline_name,
            schedule.valid_from,
            schedule.valid_to,
            schedule.no_of_seats,
            schedule.monday_operation,
            schedule.tuesday_operation,
            schedule.wednesday_operation,
            schedule.thursday_operation,
            schedule.friday_operation,
            schedule.saturday_operation,
            schedule.sunday_operation
        FROM
            schedules AS schedule
        INNER JOIN
           aircraft_types AS aircraft ON schedule.aircraft_type_id = id_aircraft_type
        INNER JOIN
            airlines AS airline ON schedule.departure_airline_id = id_airline
        WHERE
            schedule.valid_from <= %s AND schedule.valid_to >= %s
    """

    # Calculate the end date for the 10-day range
    end_range_date = valid_from + timezone.timedelta(days=9)
    if end_range_date > valid_to:
       end_range_date = valid_to
 # Call the function to get the list of dates
    date_intervals = calculate_date_between_range(valid_from.strftime('%Y-%m-%d'), valid_to.strftime('%Y-%m-%d'))
    # Execute the SQL query
    with connection.cursor() as cursor:
       cursor.execute(query, [end_range_date, valid_from])  # Fetch data only for the specified date range
       rows = cursor.fetchall()


    # Process the fetched rows and build response_data
    aircraft_types_data = defaultdict(lambda: {'aircraft_data': defaultdict(lambda: {'airlines': defaultdict(lambda: {'airline_count': 0, 'total_seats': 0}), 'total_seats': 0})})

    days_of_week = ['monday_operation', 'tuesday_operation', 'wednesday_operation', 'thursday_operation', 'friday_operation', 'saturday_operation', 'sunday_operation']

    for row in rows:
        schedule = {
            'valid_from': row[2],
            'valid_to': row[3],
            'no_of_seats': row[4]
        }
        for day_idx, day_attr in enumerate(days_of_week):
            schedule[day_attr] = bool(row[5 + day_idx])
            
        current_date = max(schedule['valid_from'], valid_from)
        end_date = min(schedule['valid_to'], valid_to)
        while current_date <= end_date:
            if schedule[days_of_week[current_date.weekday()]]:
                aircraft_name = row[0].strip()
                airline_name = row[1].strip()

                aircraft_types_data[aircraft_name]['aircraft_data'][current_date]['airlines'][airline_name]['airline_count'] += 1
                aircraft_types_data[aircraft_name]['aircraft_data'][current_date]['airlines'][airline_name]['total_seats'] += schedule['no_of_seats']
                aircraft_types_data[aircraft_name]['aircraft_data'][current_date]['total_seats'] += schedule['no_of_seats']
                current_date += timezone.timedelta(days=1)
            else:
                aircraft_name = row[0].strip()
                airline_name = row[1].strip()

                aircraft_types_data[aircraft_name]['aircraft_data'][current_date]['airlines'][airline_name]['airline_count'] = 0
                aircraft_types_data[aircraft_name]['aircraft_data'][current_date]['airlines'][airline_name]['total_seats'] = 0
                aircraft_types_data[aircraft_name]['aircraft_data'][current_date]['total_seats'] += schedule['no_of_seats']
                current_date += timezone.timedelta(days=1)
            

    restructured_data = defaultdict(lambda: {'airlines_data': defaultdict(list)})

    for aircraft_name, aircraft_data in aircraft_types_data.items():
        for day in range((valid_to - valid_from).days + 1):
            current_date = valid_from + timezone.timedelta(days=day)
            if current_date in aircraft_data['aircraft_data']:
                for airline_name, airline_info in aircraft_data['aircraft_data'][current_date]['airlines'].items():
                    entry = {
                        'date': current_date.strftime('%Y-%m-%d'),
                        'airline_count': airline_info['airline_count'],
                        'total_seats': airline_info['total_seats']
                    }
                    restructured_data[aircraft_name]['airlines_data'][airline_name].append(entry)
            else:
                entry = {
                    'date': current_date.strftime('%Y-%m-%d'),
                    'airline_count': 0,
                    'total_seats': 0
                }
                restructured_data[aircraft_name]['airlines_data'][airline_name].append(entry)
                    

    response_data = {
        'success': True,
        'respayload': [
          
        ],
          
             "date_intervals": date_intervals,  # Add the date_intervals here
        'message': 'Date-wise aircraft data is fetched successfully',
    }

    for aircraft_name, aircraft_data in restructured_data.items():
        aircraft_entry = {
            'aircraft_type': aircraft_name,
            'valid_from': valid_from,
            'valid_to': valid_to,
            'aircraft_data': [],
           
        }

        for airline_name, airline_info in aircraft_data['airlines_data'].items():
            airline_entry = {
                'airline_name': airline_name,
                'total_seats_count': 0,  # Initialize overall seats count
                'total_airlines_count': 0,  # Initialize overall airlines count
                'dates': airline_info
            }

            # Calculate overall counts for this airline
            for date_entry in airline_info:
                airline_entry['total_seats_count'] += date_entry['total_seats']
                airline_entry['total_airlines_count'] += date_entry['airline_count']

            aircraft_entry['aircraft_data'].append(airline_entry)

        response_data['respayload'].append(aircraft_entry)

    return JsonResponse(response_data)


@api_view(['GET'])
def airline_paxhandling_report(request):
    valid_from = request.GET.get('valid_from', None)
    valid_to = request.GET.get('valid_to', None)
    valid_from_date = datetime.strptime(valid_from, '%Y-%m-%d').date() if valid_from else None
    valid_to_date = datetime.strptime(valid_to, '%Y-%m-%d').date() if valid_to else None
    airline_id = request.GET.getlist('airline_id', [])
    day_wise = request.GET.get('day_wise').lower() == 'true'
    filter_by = request.GET.get('filter_by')
    start_date = ''
    end_date = ''
    date_query = ''
    airline_id_query = ''
    format_string = '%Y-%m-%d'
    interval_type = ""
    join_condition_hourly = ''

    airline_id_tuple = ', '.join(str(id) for id in airline_id)
    print(type(day_wise))
    # calculating dates for getting the schedule date 
    if not valid_from and not valid_to:
        with connection.cursor() as cursor:
            cursor.execute("SELECT MIN(valid_from) FROM schedules;")
            result = cursor.fetchone()
            min_date = result[0].strftime(format_string) if result[0] else date.today().strftime(format_string)
            start_date = min_date
            end_date = min_date
    elif not valid_from or not valid_to:
        start_date = valid_from if not valid_to else valid_to
        end_date = valid_from if not valid_to else valid_to
    elif valid_from and valid_to:
        start_date = valid_from
        end_date = valid_to

    # calculating date range for individual dates
    date_array = calculate_date_between_range(start_date, end_date)

    # forming queries
    # forming the date query to be appended for day wise query execution
    for index, curr_date in enumerate(date_array):
        if index == 0:
            date_query = date_query + f"SELECT '{curr_date}'::date AS custom_date"
            if len(date_array) > 1:
                date_query = date_query + " UNION ALL"
        elif index == len(date_array) - 1:
            date_query = date_query + f" SELECT '{curr_date}'::date"
        else:
            date_query = date_query + f" SELECT '{curr_date}'::date UNION ALL"

    #forming airline query
    for airline_index, curr_id in enumerate(airline_id):
        if airline_index == 0:
            airline_id_query = airline_id_query + f" WHERE id_airline IN ({curr_id}"
            if len(airline_id) <= 1:
                airline_id_query = airline_id_query + ")"
        elif airline_index == len(airline_id) - 1:
            airline_id_query = airline_id_query + f",{curr_id})"
        else:
            airline_id_query = airline_id_query + f",{curr_id}"
    
    if(airline_id_tuple != ''):
        if filter_by == 'arrival':
            airline_condition = f"AND schedules.arrival_airline_id IN ({airline_id_tuple})"
        elif filter_by == 'departure':
            airline_condition = f"AND schedules.departure_airline_id IN ({airline_id_tuple})"
        else:
            airline_condition = f"""
                AND (
                    schedules.arrival_airline_id IN ({airline_id_tuple}) OR 
                    schedules.departure_airline_id IN ({airline_id_tuple})
                )
            """
    else:
        airline_condition = ''
            
    if filter_by == 'arrival':
        join_condition = "LEFT JOIN airlines AS airline ON schedules.arrival_airline_id = airline.id_airline"
    elif filter_by == 'departure':
        join_condition = "LEFT JOIN airlines AS airline ON schedules.departure_airline_id = airline.id_airline"
    else:
        join_condition = "LEFT JOIN airlines AS airline ON schedules.arrival_airline_id = airline.id_airline OR schedules.departure_airline_id = airline.id_airline"

    day_wise_query = """
        WITH RECURSIVE date_range AS (
            SELECT 
                id_schedule,
                CAST(valid_from AS timestamp) as date_value
            FROM
                schedules
            UNION ALL
            SELECT
                dr.id_schedule,
                dr.date_value + INTERVAL '1' DAY
            FROM
                date_range dr
            JOIN
                schedules s ON dr.id_schedule = s.id_schedule
            WHERE
                dr.date_value < (SELECT MAX(CAST(valid_to AS date)) FROM schedules WHERE id_schedule = dr.id_schedule)
        ),
        custom_date_range AS (%s),
        individual_schedule AS (
            SELECT
                schedules.id_schedule,
                schedules.no_of_seats,
                CAST(schedules.valid_from AS timestamp) AS valid_from_timestamp,
                CAST(schedules.valid_to AS timestamp) AS valid_to_timestamp,
                airline.airline_name,
                airline.id_airline,
                generate_series(CAST(schedules.valid_from AS timestamp), CAST(schedules.valid_to AS timestamp), '1 day')::date AS date_value
            FROM
                schedules
            %s
            %s
        )
        SELECT
            t.id_airline,
            t.airline_name,
            json_agg(json_build_object( 'date', date_value, 'count', event_count) ORDER BY date_value) AS date_range
        FROM (
            SELECT
                v.id_airline,
                v.airline_name,
                date_value,
                SUM(no_of_seats) AS event_count
            FROM
                custom_date_range c
            CROSS JOIN
                (SELECT DISTINCT id_schedule, id_airline, airline_name, valid_from_timestamp, valid_to_timestamp FROM individual_schedule) v
            LEFT JOIN individual_schedule i ON c.custom_date = i.date_value AND v.id_schedule = i.id_schedule AND v.id_airline = i.id_airline
            WHERE
                i.date_value BETWEEN v.valid_from_timestamp::date AND v.valid_to_timestamp::date
            GROUP BY
                v.id_airline, date_value, v.airline_name
        ) AS t
        GROUP BY
            t.id_airline, t.airline_name
        ORDER BY
            t.id_airline

    """
    hour_wise_query = f"""
        CREATE TEMPORARY TABLE IF NOT EXISTS TempHourlyAirlineScheduleCounts (
            id_airline TEXT,
            airline_name TEXT,
            airline_code TEXT,
            hour_interval TEXT,
            total_seats INT
        );

        INSERT INTO TempHourlyAirlineScheduleCounts
        SELECT
            origin_airline.id_airline AS id_airline,
            origin_airline.airline_name AS airline_name,
            origin_airline.airline_code AS airline_code,
            CASE
                WHEN departure_time >= '0000' AND departure_time <= '0059' THEN '00:00 - 01:00'
                WHEN departure_time >= '0100' AND departure_time <= '0159' THEN '01:00 - 02:00'
                WHEN departure_time >= '0200' AND departure_time <= '0259' THEN '02:00 - 03:00'
                WHEN departure_time >= '0300' AND departure_time <= '0359' THEN '03:00 - 04:00'
                WHEN departure_time >= '0400' AND departure_time <= '0459' THEN '04:00 - 05:00'
                WHEN departure_time >= '0500' AND departure_time <= '0559' THEN '05:00 - 06:00'
                WHEN departure_time >= '0600' AND departure_time <= '0659' THEN '06:00 - 07:00'
                WHEN departure_time >= '0700' AND departure_time <= '0759' THEN '07:00 - 08:00'
                WHEN departure_time >= '0800' AND departure_time <= '0859' THEN '08:00 - 09:00'
                WHEN departure_time >= '0900' AND departure_time <= '0959' THEN '09:00 - 10:00'
                WHEN departure_time >= '1000' AND departure_time <= '1059' THEN '10:00 - 11:00'
                WHEN departure_time >= '1100' AND departure_time <= '1159' THEN '11:00 - 12:00'
                WHEN departure_time >= '1200' AND departure_time <= '1259' THEN '12:00 - 13:00'
                WHEN departure_time >= '1300' AND departure_time <= '1359' THEN '13:00 - 14:00'
                WHEN departure_time >= '1400' AND departure_time <= '1459' THEN '14:00 - 15:00'
                WHEN departure_time >= '1500' AND departure_time <= '1559' THEN '15:00 - 16:00'
                WHEN departure_time >= '1600' AND departure_time <= '1659' THEN '16:00 - 17:00'
                WHEN departure_time >= '1700' AND departure_time <= '1759' THEN '17:00 - 18:00'
                WHEN departure_time >= '1800' AND departure_time <= '1859' THEN '18:00 - 19:00'
                WHEN departure_time >= '1900' AND departure_time <= '1959' THEN '19:00 - 20:00'
                WHEN departure_time >= '2000' AND departure_time <= '2059' THEN '20:00 - 21:00'
                WHEN departure_time >= '2100' AND departure_time <= '2159' THEN '21:00 - 22:00'
                WHEN departure_time >= '2200' AND departure_time <= '2259' THEN '22:00 - 23:00'
                WHEN departure_time >= '2300' AND departure_time <= '2359' THEN '23:00 - 24:00'
                ELSE 'Unknown'
            END AS hour_interval,
            SUM(no_of_seats) AS total_seats
        FROM schedules
        {'JOIN airlines origin_airline ON arrival_airline_id = id_airline' if filter_by == 'arrival' else 'JOIN airlines origin_airline ON departure_airline_id = id_airline' if filter_by == 'departure' else 'JOIN airlines origin_airline ON (arrival_airline_id = id_airline OR departure_airline_id = id_airline)'}
        WHERE 
            ( valid_from <= %s::DATE AND valid_to >= %s::DATE )
            {airline_condition}
        GROUP BY
            id_airline,
            arrival_airline_id,
            airline_name,
            airline_code,
            hour_interval;

        SELECT
            id_airline,
            airline_name,
            json_agg(hourly_info) AS date_range
        FROM (
            SELECT
                id_airline,
                airline_name,
                hour_interval,
                json_build_object(
                    'date', hour_interval,
                    'count', total_seats
                ) AS hourly_info
            FROM
                TempHourlyAirlineScheduleCounts
        ) AS hourly_info_subquery
        GROUP BY
            id_airline,
            airline_name
        ORDER BY
            id_airline
    """
    
    # Execute the SQL query
    with connection.cursor() as cursor:
        
        args = (date_query,join_condition, airline_id_query)
        if(start_date != end_date or day_wise):
            # for date range
            interval_type = "day"
            cursor.execute(day_wise_query % args)
            columns = [desc[0] for desc in cursor.description]
            result = [dict(zip(columns, row)) for row in cursor.fetchall()]
        else:
            # for single date
            # if airline_id == []:
            interval_type = "hour"
            # cursor.execute(build_hour_wise_query(start_date, filter_by, airline_id_tuple))
            date_intervals = ['00:00 - 01:00', '01:00 - 02:00', '02:00 - 03:00', '03:00 - 04:00', '04:00 - 05:00', '05:00 - 06:00', '06:00 - 07:00', '07:00 - 08:00', '08:00 - 09:00', '09:00 - 10:00', '10:00 - 11:00', '11:00 - 12:00', '12:00 - 13:00', '13:00 - 14:00', '14:00 - 15:00', '15:00 - 16:00', '16:00 - 17:00', '17:00 - 18:00', '18:00 - 19:00', '19:00 - 20:00', '20:00 - 21:00', '21:00 - 22:00', '22:00 - 23:00', '23:00 - 24:00']
            cursor.execute(hour_wise_query, [valid_from, valid_to,])
            columns = [desc[0] for desc in cursor.description]
            result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        # result = cursor.fetchall()
        total_data = {
            "airline_name": "Total",
            "date_range": []
        }
        # columns = [desc[0] for desc in cursor.description]
        
        # # checking if the date single or multiple
        # if(start_date == end_date and day_wise == False):
        #     data = []
        #     for row in cursor.fetchall():
        #         data.append(dict(zip(columns, row)))
        # else:
        #     result = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # calculate the total counts for the columns
        def add_total_count(data, curr_date):
            total_count = 0

            for curr_airline in data:
                curr_airline_date_range = curr_airline["date_range"]
                curr_date_count = list(filter(lambda date: date["date"] == curr_date, curr_airline_date_range))
                if curr_date_count and len(curr_date_count) > 0:
                    total_count = total_count + curr_date_count[0]['count']
                else:
                    total_count = total_count + 0

            return total_count
    
        hoursArray = []
        # if the it is just a single date then we need to append the data as hours 
        if(start_date == end_date and day_wise == False):
            # finaldata = count_no_of_seats_in_flights_by_hour(result),
            for hour in range(24):
                hoursArray.append(str(convert_to_time_format(hour)) + ' - ' + str(convert_to_time_format(hour + 1)))
                total_for_that_day = add_total_count(result, str(convert_to_time_format(hour)) + ' - ' + str(convert_to_time_format(hour + 1)),)
                total_data['date_range'].append({
                    "date": str(convert_to_time_format(hour)) + ' - ' + str(convert_to_time_format(hour + 1)),
                    "count": total_for_that_day
                })
            result.append(total_data)
        else:
        # calculate total for all the flights
            for curr_date in date_array:
                total_for_that_day = add_total_count(result, curr_date)
                total_data['date_range'].append({
                    "date": curr_date,
                    "count": total_for_that_day
                })
        
            result.append(total_data)
    response_data = {
            'success': True,
            'message': 'Data fetched successfully',
            'respayload': {
                'airlines_data': result,
                'date_range': date_intervals if (start_date == end_date and day_wise == False) else date_array,
                "type": interval_type,
                # 'result':result
            }
        }
    return JsonResponse(response_data, safe=False)

def getAirlinesList(request):
    if request.method == 'GET':
        # Write the raw SQL query
        query = """
        SELECT DISTINCT a.airline_name, a.airline_code, a.logo_image
        FROM airlines a
        INNER JOIN schedules s ON a.id_airline = s.arrival_airline_id OR a.id_airline = s.departure_airline_id
        """

        # Execute the query
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        # Transform the raw result into desired response structure
        response_data = {
            'success': True,
            'respayload': [],
            'message': 'airlines data is fetched successfully',
        }

        for row in result:
            airline_name, airline_code, airline_logo = row
            airline_info = {
                'airline_name': airline_name,
                'airline_code': airline_code,
                'airline_logo': airline_logo,
            }
            response_data['respayload'].append(airline_info)

        return JsonResponse(response_data)
    
    
def getAircraftsList(request):
    if request.method == 'GET':
        # Write the raw SQL query
        query = """
        SELECT DISTINCT at.aircraft_name, at.aircraft_code, at.aircraft_logo
        FROM aircraft_types at
        INNER JOIN schedules s ON at.id_aircraft_type = s.aircraft_type_id
        """

        # Execute the query
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        # Transform the raw result into desired response structure
        response_data = {
            'success': True,
            'respayload': [],
            'message': 'aircrafts data is fetched successfully',
        }

        for row in result:
            aircraft_name, aircraft_code, aircraft_logo = row
            aircraft_info = {
                'aircraft_name': aircraft_name,
                'aircraft_code': aircraft_code,
                'aircraft_logo': aircraft_logo,
            }
            response_data['respayload'].append(aircraft_info)

        return JsonResponse(response_data)


def aircraftBasedOvernightParkingCount(request):
    current_date = timezone.now().date()

    valid_from_str = request.GET.get('valid_from')
    valid_to_str = request.GET.get('valid_to')

    if valid_from_str:
        valid_from = datetime.strptime(valid_from_str, '%Y-%m-%d').date()
    else:
        valid_from, valid_to = get_valid_date_range(current_date)
        if valid_from and valid_to:
            if valid_from <= current_date <= valid_to:
                valid_from = current_date
                valid_to = valid_from + timezone.timedelta(days=9)
            else:
                earliest_date, _ = get_valid_date_range(current_date)
                valid_from = earliest_date
                valid_to = earliest_date + timezone.timedelta(days=9)

    if valid_to_str:
        valid_to = datetime.strptime(valid_to_str, '%Y-%m-%d').date()
   
      # Construct the SQL query
    query = """
     WITH DateRange AS (
        SELECT generate_series(%s::DATE, %s::DATE, '1 DAY')::DATE AS current_date
     )
     SELECT
        aircraft.aircraft_name,
        airline.airline_name,
        DateRange.current_date AS date,
        SUM(CASE
            WHEN (
                (schedules.monday_operation AND EXTRACT(DOW FROM DateRange.current_date) = 1) OR
                (schedules.tuesday_operation AND EXTRACT(DOW FROM DateRange.current_date) = 2) OR
                (schedules.wednesday_operation AND EXTRACT(DOW FROM DateRange.current_date) = 3) OR
                (schedules.thursday_operation AND EXTRACT(DOW FROM DateRange.current_date) = 4) OR
                (schedules.friday_operation AND EXTRACT(DOW FROM DateRange.current_date) = 5) OR
                (schedules.saturday_operation AND EXTRACT(DOW FROM DateRange.current_date) = 6) OR
                (schedules.sunday_operation AND EXTRACT(DOW FROM DateRange.current_date) = 0)
            ) AND schedules.overnight_parking THEN 1
            ELSE 0
        END) AS overnight_parking_count,
        SUM(schedules.no_of_seats) AS total_seats
    FROM
        DateRange
    JOIN
        schedules ON DateRange.current_date BETWEEN schedules.valid_from AND schedules.valid_to
    JOIN
        aircraft_types AS aircraft ON schedules.aircraft_type_id = aircraft.id_aircraft_type
    JOIN
        airlines AS airline ON schedules.departure_airline_id = airline.id_airline
    GROUP BY
        aircraft.aircraft_name,
        airline.airline_name,
        DateRange.current_date
    ORDER BY
        aircraft.aircraft_name,
        airline.airline_name,
        DateRange.current_date;
    """

     # Calculate the end date for the 10-day range
    end_range_date = valid_from + timezone.timedelta(days=9)
    if end_range_date > valid_to:
       end_range_date = valid_to

    # Call the function to get the list of dates
    date_intervals = calculate_date_between_range(valid_from.strftime('%Y-%m-%d'), valid_to.strftime('%Y-%m-%d'))

    with connection.cursor() as cursor:
       cursor.execute(query, [valid_from, valid_to])
       rows = cursor.fetchall()

   # Process the fetched rows and build response_data
    response_data = {
        'success': True,
        
        'respayload': [],
        "date_intervals": date_intervals,  # Add the date_intervals here
        'message': 'Date-wise aircraft data is fetched successfully',
    }

    aircraft_types_data = defaultdict(lambda: {'airlines_data': defaultdict(list)})

    for row in rows:
        aircraft_name = row[0].strip()
        airline_name = row[1].strip()
        current_date = row[2]
        overnight_parking_count = row[3]
        total_seats = row[4]

        entry = {
            'date': current_date.strftime('%Y-%m-%d'),
            'overnight_parking_count': overnight_parking_count,
        }
        aircraft_types_data[aircraft_name]['airlines_data'][airline_name].append(entry)

    for aircraft_name, aircraft_data in aircraft_types_data.items():
        aircraft_entry = {
            'aircraft_type': aircraft_name,
            'valid_from': valid_from.strftime('%Y-%m-%d'),
            'valid_to': valid_to.strftime('%Y-%m-%d'),
            'airline_data': [],
            
        }

        for airline_name, airline_info in aircraft_data['airlines_data'].items():
            consolidated_dates = defaultdict(int)  # To store consolidated data for each date

            for entry in airline_info:
                date_str = entry['date']
                overnight_parking_count = entry['overnight_parking_count']
                consolidated_dates[date_str] += overnight_parking_count

            consolidated_airline_info = []

            for date, parking_count in consolidated_dates.items():
                consolidated_airline_info.append({
                    'date': date,
                    'overnight_parking_count': parking_count,
                })

            airline_entry = {
                'airline_name': airline_name,
                'dates': consolidated_airline_info,
               
            }

            aircraft_entry['airline_data'].append(airline_entry)

        response_data['respayload'].append(aircraft_entry)

    return JsonResponse(response_data)



@api_view(['GET'])
def airline_arrivalsdepartures_report(request):
    date = request.GET.get('date', None)
    valid_from_date = datetime.strptime(date, '%Y-%m-%d').date() if date else None
    airline_id = request.GET.getlist('airline_id', [])
    day_wise = request.GET.get('day_wise').lower() == 'true'
    filter_by = request.GET.get('filter_by')
    format_string = '%Y-%m-%d'
    interval_type = ""

    airline_id_tuple = ', '.join(str(id) for id in airline_id)
    print(type(day_wise))
    # calculating dates for getting the schedule date 
    if not date:
        with connection.cursor() as cursor:
            cursor.execute("SELECT MIN(valid_from) FROM schedules;")
            result = cursor.fetchone()
            min_date = result[0].strftime(format_string) if result[0] else date.today().strftime(format_string)
            date = min_date
    elif date:
        date = date
    
    if(airline_id_tuple != ''):
        if filter_by == 'arrival':
            airline_condition = f"AND schedules.arrival_airline_id IN ({airline_id_tuple})"
        elif filter_by == 'departure':
            airline_condition = f"AND schedules.departure_airline_id IN ({airline_id_tuple})"
        else:
            airline_condition = f"""
                AND (
                    schedules.arrival_airline_id IN ({airline_id_tuple}) OR 
                    schedules.departure_airline_id IN ({airline_id_tuple})
                )
            """
    else:
        airline_condition = ''
            
    if filter_by == 'arrival':
        join_condition = "LEFT JOIN airlines AS airline ON schedules.arrival_airline_id = airline.id_airline"
    elif filter_by == 'departure':
        join_condition = "LEFT JOIN airlines AS airline ON schedules.departure_airline_id = airline.id_airline"
    else:
        join_condition = "LEFT JOIN airlines AS airline ON schedules.arrival_airline_id = airline.id_airline OR schedules.departure_airline_id = airline.id_airline"

    hour_wise_query = f"""
    CREATE TEMPORARY TABLE IF NOT EXISTS TempHourlyAirlineScheduleCounts (
        id_airline_origin TEXT,
        id_airline_departure TEXT,
        airline_name_origin TEXT,
        airline_name_departure TEXT,
        airline_code_origin TEXT,
        airline_code_departure TEXT,
        hour_interval_origin TEXT,
        hour_interval_departure TEXT,
        schedule_count_origin INT,
        schedule_count_departure INT
    );

    INSERT INTO TempHourlyAirlineScheduleCounts
    SELECT
        origin_airline.id_airline AS id_airline_origin,
        departure_airline.id_airline AS id_airline_departure,
        origin_airline.airline_name AS airline_name_origin,
        departure_airline.airline_name AS airline_name_departure,
        origin_airline.airline_code AS airline_code_origin,
        departure_airline.airline_code AS airline_code_departure,
        CASE
            WHEN arrival_time >= '0000' AND arrival_time <= '0059' THEN '00:00 - 01:00'
            WHEN arrival_time >= '0100' AND arrival_time <= '0159' THEN '01:00 - 02:00'
            WHEN arrival_time >= '0200' AND arrival_time <= '0259' THEN '02:00 - 03:00'
            WHEN arrival_time >= '0300' AND arrival_time <= '0359' THEN '03:00 - 04:00'
            WHEN arrival_time >= '0400' AND arrival_time <= '0459' THEN '04:00 - 05:00'
            WHEN arrival_time >= '0500' AND arrival_time <= '0559' THEN '05:00 - 06:00'
            WHEN arrival_time >= '0600' AND arrival_time <= '0659' THEN '06:00 - 07:00'
            WHEN arrival_time >= '0700' AND arrival_time <= '0759' THEN '07:00 - 08:00'
            WHEN arrival_time >= '0800' AND arrival_time <= '0859' THEN '08:00 - 09:00'
            WHEN arrival_time >= '0900' AND arrival_time <= '0959' THEN '09:00 - 10:00'
            WHEN arrival_time >= '1000' AND arrival_time <= '1059' THEN '10:00 - 11:00'
            WHEN arrival_time >= '1100' AND arrival_time <= '1159' THEN '11:00 - 12:00'
            WHEN arrival_time >= '1200' AND arrival_time <= '1259' THEN '12:00 - 13:00'
            WHEN arrival_time >= '1300' AND arrival_time <= '1359' THEN '13:00 - 14:00'
            WHEN arrival_time >= '1400' AND arrival_time <= '1459' THEN '14:00 - 15:00'
            WHEN arrival_time >= '1500' AND arrival_time <= '1559' THEN '15:00 - 16:00'
            WHEN arrival_time >= '1600' AND arrival_time <= '1659' THEN '16:00 - 17:00'
            WHEN arrival_time >= '1700' AND arrival_time <= '1759' THEN '17:00 - 18:00'
            WHEN arrival_time >= '1800' AND arrival_time <= '1859' THEN '18:00 - 19:00'
            WHEN arrival_time >= '1900' AND arrival_time <= '1959' THEN '19:00 - 20:00'
            WHEN arrival_time >= '2000' AND arrival_time <= '2059' THEN '20:00 - 21:00'
            WHEN arrival_time >= '2100' AND arrival_time <= '2159' THEN '21:00 - 22:00'
            WHEN arrival_time >= '2200' AND arrival_time <= '2259' THEN '22:00 - 23:00'
            WHEN arrival_time >= '2300' AND arrival_time <= '2359' THEN '23:00 - 24:00'
            ELSE 'Unknown'
        END AS hour_interval_origin,
        CASE
            WHEN departure_time >= '0000' AND departure_time <= '0059' THEN '00:00 - 01:00'
            WHEN departure_time >= '0100' AND departure_time <= '0159' THEN '01:00 - 02:00'
            WHEN departure_time >= '0200' AND departure_time <= '0259' THEN '02:00 - 03:00'
            WHEN departure_time >= '0300' AND departure_time <= '0359' THEN '03:00 - 04:00'
            WHEN departure_time >= '0400' AND departure_time <= '0459' THEN '04:00 - 05:00'
            WHEN departure_time >= '0500' AND departure_time <= '0559' THEN '05:00 - 06:00'
            WHEN departure_time >= '0600' AND departure_time <= '0659' THEN '06:00 - 07:00'
            WHEN departure_time >= '0700' AND departure_time <= '0759' THEN '07:00 - 08:00'
            WHEN departure_time >= '0800' AND departure_time <= '0859' THEN '08:00 - 09:00'
            WHEN departure_time >= '0900' AND departure_time <= '0959' THEN '09:00 - 10:00'
            WHEN departure_time >= '1000' AND departure_time <= '1059' THEN '10:00 - 11:00'
            WHEN departure_time >= '1100' AND departure_time <= '1159' THEN '11:00 - 12:00'
            WHEN departure_time >= '1200' AND departure_time <= '1259' THEN '12:00 - 13:00'
            WHEN departure_time >= '1300' AND departure_time <= '1359' THEN '13:00 - 14:00'
            WHEN departure_time >= '1400' AND departure_time <= '1459' THEN '14:00 - 15:00'
            WHEN departure_time >= '1500' AND departure_time <= '1559' THEN '15:00 - 16:00'
            WHEN departure_time >= '1600' AND departure_time <= '1659' THEN '16:00 - 17:00'
            WHEN departure_time >= '1700' AND departure_time <= '1759' THEN '17:00 - 18:00'
            WHEN departure_time >= '1800' AND departure_time <= '1859' THEN '18:00 - 19:00'
            WHEN departure_time >= '1900' AND departure_time <= '1959' THEN '19:00 - 20:00'
            WHEN departure_time >= '2000' AND departure_time <= '2059' THEN '20:00 - 21:00'
            WHEN departure_time >= '2100' AND departure_time <= '2159' THEN '21:00 - 22:00'
            WHEN departure_time >= '2200' AND departure_time <= '2259' THEN '22:00 - 23:00'
            WHEN departure_time >= '2300' AND departure_time <= '2359' THEN '23:00 - 24:00'
            ELSE 'Unknown'
        END AS hour_interval_departure,
        COUNT(*) AS schedule_count_origin,
        COUNT(*) AS schedule_count_departure
    FROM
        schedules
    JOIN airlines origin_airline ON (arrival_airline_id = origin_airline.id_airline)
    JOIN airlines departure_airline ON (departure_airline_id = departure_airline.id_airline)
    WHERE 
        (valid_from <= %s::DATE AND valid_to >= %s::DATE)
        {airline_condition}
    GROUP BY
        id_airline_origin,
        id_airline_departure,
        airline_name_origin,
        airline_name_departure,
        airline_code_origin,
        airline_code_departure,
        hour_interval_origin,
        hour_interval_departure;

    WITH HourlyInfoCTE AS (
        SELECT
            id_airline_origin,
            id_airline_departure,
            airline_name_origin,
            airline_name_departure,
            hour_interval_origin,
            hour_interval_departure,
            json_build_object(
                'date', hour_interval_origin,
                'count', SUM(schedule_count_origin) 
            ) AS hourly_info_origin,
            json_build_object(
                'date', hour_interval_departure,
                'count', SUM(schedule_count_departure)
            ) AS hourly_info_departure
        FROM
            TempHourlyAirlineScheduleCounts
        GROUP BY
            id_airline_origin,
            id_airline_departure,
            airline_name_origin,
            airline_name_departure,
            hour_interval_origin,
            hour_interval_departure
    )

SELECT
    id_airline_origin,
    id_airline_departure,
    airline_name_origin,
    airline_name_departure,
    SUM(count_arrival) AS total_arrival,
    SUM(count_departure) AS total_departure,
    SUM(count_total) AS total,
    JSON_AGG(
        JSON_BUILD_OBJECT(
            'date', date_range,
            'count', count_arrival
        )
    ) FILTER (WHERE count_arrival > 0) AS date_range_arrival,
    JSON_AGG(
        JSON_BUILD_OBJECT(
            'date', date_range,
            'count', count_departure
        )
    ) FILTER (WHERE count_departure > 0) AS date_range_departure,
    JSON_AGG(
        JSON_BUILD_OBJECT(
            'date', date_range,
            'count', count_arrival + count_departure
        )
    ) FILTER (WHERE count_arrival + count_departure > 0) AS date_range_total
FROM (
    SELECT
        id_airline_origin,
        id_airline_departure,
        airline_name_origin,
        airline_name_departure,
        date_range,
        SUM(count_arrival) AS count_arrival,
        SUM(count_departure) AS count_departure,
        SUM(count_arrival) + SUM(count_departure) AS count_total
    FROM (
     SELECT
            id_airline_origin,
            id_airline_departure,
            airline_name_origin,
            airline_name_departure,
            hour_interval_departure AS date_range,
            SUM((hourly_info_departure->>'count')::INT) AS count_departure,
            0 AS count_arrival
        FROM HourlyInfoCTE
        GROUP BY
            id_airline_origin,
            id_airline_departure,
            airline_name_origin,
            airline_name_departure,
            hour_interval_departure
      
        UNION ALL
         SELECT
            id_airline_origin,
            id_airline_departure,
            airline_name_origin,
            airline_name_departure,
            hour_interval_origin AS date_range,
            0 AS count_arrival,
            SUM((hourly_info_origin->>'count')::INT) AS count_arrival
        FROM HourlyInfoCTE
        GROUP BY
            id_airline_origin,
            id_airline_departure,
            airline_name_origin,
            airline_name_departure,
            hour_interval_origin
    ) AS subquery
    GROUP BY
        id_airline_origin,
        id_airline_departure,
        airline_name_origin,
        airline_name_departure,
        date_range
) AS t
GROUP BY
    id_airline_origin,
    id_airline_departure,
    airline_name_origin,
    airline_name_departure
HAVING
    SUM(count_arrival) + SUM(count_departure) > 0 -- Only include airlines with non-zero totals
ORDER BY
    id_airline_origin;


"""

    
    # Execute the SQL query
    with connection.cursor() as cursor:
        # for single date
        # if airline_id == []:
        interval_type = "hour"
        # cursor.execute(build_hour_wise_query(start_date, filter_by, airline_id_tuple))
        date_intervals = ['00:00 - 01:00', '01:00 - 02:00', '02:00 - 03:00', '03:00 - 04:00', '04:00 - 05:00', '05:00 - 06:00', '06:00 - 07:00', '07:00 - 08:00', '08:00 - 09:00', '09:00 - 10:00', '10:00 - 11:00', '11:00 - 12:00', '12:00 - 13:00', '13:00 - 14:00', '14:00 - 15:00', '15:00 - 16:00', '16:00 - 17:00', '17:00 - 18:00', '18:00 - 19:00', '19:00 - 20:00', '20:00 - 21:00', '21:00 - 22:00', '22:00 - 23:00', '23:00 - 24:00']
        cursor.execute(hour_wise_query, [date, date,])
        columns = [desc[0] for desc in cursor.description]
        result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        # result = cursor.fetchall()
        total_data = {
            "airline_name": "Total",
            "date_range": []
        }
        # calculate the total counts for the columns
        def add_total_count(data, curr_date):
            total_count = 0

            for curr_airline in data:
                curr_airline_date_range = curr_airline["date_range"]
                curr_date_count = list(filter(lambda date: date["date"] == curr_date, curr_airline_date_range))
                if curr_date_count and len(curr_date_count) > 0:
                    total_count = total_count + curr_date_count[0]['count']
                else:
                    total_count = total_count + 0

            return total_count
    
        hoursArray = []
        
        # finaldata = count_no_of_seats_in_flights_by_hour(result),
        # for hour in range(24):
        #     hoursArray.append(str(convert_to_time_format(hour)) + ' - ' + str(convert_to_time_format(hour + 1)))
        #     total_for_that_day = add_total_count(result, str(convert_to_time_format(hour)) + ' - ' + str(convert_to_time_format(hour + 1)),)
        #     total_data['date_range'].append({
        #         "date": str(convert_to_time_format(hour)) + ' - ' + str(convert_to_time_format(hour + 1)),
        #         "count": total_for_that_day
        #     })
        # result.append(total_data)
    response_data = {
            'success': True,
            'message': 'Data fetched successfully',
            'respayload': {
                'airlines_data': result,
                'date_range': date_intervals,
                "type": interval_type,
                # 'result':result
            }
        }
    return JsonResponse(response_data, safe=False)