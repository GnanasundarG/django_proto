from rest_framework.response import Response

def generate_error_response(exception, type=""):
    status_code = getattr(exception, 'status_code', 500)  # If no status_code attribute, default to 500 (Internal Server Error)
    error_message = str(exception)
    return Response({
        "status": "error",
        "success": False,
        "code": status_code,
        "message": error_message,
        "type": type,
    }, status=status_code)

def manual_error_response(code,message, type):
    return Response({
        "status": "error",
        "success": False,
        "code": code,
        "message": message,
        "type": type,
    }, status=code)
 
def manual_error_response_with_json_response(code,message, type):
    return Response({
        "status": "error",
        "success": False,
        "code": code,
        "message": message,
        "type": type,
    }, status=code)