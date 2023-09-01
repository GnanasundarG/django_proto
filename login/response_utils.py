from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

def generate_error_response(exception, code = "", type=""):
    status_code = code if code != "" else getattr(exception, 'status_code', 500)  # If no status_code attribute, default to 500 (Internal Server Error)
    error_message = str(exception)
    response = Response(
         data = {
            "status": "error",
            "success": False,
            "code": status_code,
            "message": error_message,
            "type": type,
        },
        status = status_code
    )
    response.accepted_renderer = JSONRenderer()
    response.accepted_media_type = "application/json"
    response.renderer_context = {}
    response.render()
    return response

def manual_error_response(status_code, message, type):
    response_data = {
        'success': False,
        'error': {
            'status_code': status_code,
            'message': message,
            'type': type,
        }
    }
    return JsonResponse(response_data, status=status_code)
 
def manual_error_response_with_json_response(code,message, type):
    return Response({
        "status": "error",
        "success": False,
        "code": code,
        "message": message,
        "type": type,
    }, status=code)