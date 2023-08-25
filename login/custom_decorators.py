from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from login.response_utils import generate_error_response

def validate_msg_params(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.method == 'GET':
            msg = request.GET.get('msg')
            if msg is None:
                return generate_error_response(
                    Exception("The 'msg' query parameter is required."),
                    type="Validation Error",
                )
        
        elif request.method == 'POST':
            msg = request.data.get('msg')
            if msg is None:
                return generate_error_response(
                    Exception("The 'msg' field is required in the request body."),
                    type="Validation Error",
                )
                
        # # Check if 'user_id' parameter is present and exists in the database
        # user_id = request.data.get('user_id')  # Assuming 'user_id' is passed in the POST request body
        # if user_id:
        #     try:
        #         user = User.objects.get(id=user_id)
        #     except User.DoesNotExist:
        #         return generate_error_response(
        #             Exception(f"User with ID {user_id} does not exist."),
        #             type="Validation Error",
        #         )
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view
