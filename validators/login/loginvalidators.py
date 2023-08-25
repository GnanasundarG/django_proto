import re
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from login.models import users, role
from login.serializers import RoleSerializer
from login.response_utils import manual_error_response

def is_valid_email(email):
    # Regular expression for basic email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)

def login_validate(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        role_code = request.data.get("role_code") 

        validation_errors = []

        if email is None or not is_valid_email(email):
            validation_errors.append("Invalid email format")

        if password is None or not isinstance(password, str) or len(password) < 8:
            validation_errors.append("Password must be a string of at least 8 characters")

        if not any(char.isupper() for char in password) or not any(char.isdigit() for char in password) or not any(char in '!@#$%^&*()_-+={}[]|\:;"<>,.?/~`' for char in password):
            validation_errors.append("Password must contain at least one uppercase letter, one digit, and one special character")

        if role_code is None:
            validation_errors.append("Role code is required")

        elif role_code:
            role_data = role.objects.all().filter(role_code=role_code).count()
            if role_data < 1:
                validation_errors.append("Invalid role code")

        if validation_errors:
            return manual_error_response(401, "Invalid credentials", "")

        return view_func(request, *args, **kwargs)

    return _wrapped_view
