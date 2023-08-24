# Create your views here.
import bcrypt
from django.http import JsonResponse
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from login.custom_decorators import validate_msg_params
from login.models import role, users
from login.serializers import RoleSerializer
from login.serializers import UserSerializer
from tokens.tokens import create_jwt_pair_for_user

from validators.login.loginvalidators import login_validate
from .response_utils import generate_error_response, manual_error_response 
from rest_framework import generics, status
from rest_framework.views import APIView
import json



@api_view(['POST'])
@login_validate
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")
    role_code = request.data.get("role_code")  # Assuming the role_code is provided in the request
    # hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=10))
    try:
        user = users.objects.get(email=email)
        if user.role.role_code == role_code:
            # Role code matches, now check the password
            if bcrypt.checkpw(password.encode('utf8'), user.password.encode('utf8')):
                # Passwords match, proceed with login
                serializer = UserSerializer(user)
                tokens = create_jwt_pair_for_user(user)
                return Response({'message': 'Login successful', 'success': True, 'respayload': tokens}, status=status.HTTP_200_OK)
            else:
                return manual_error_response(401, "Invalid credentials", "")
        else:
            return manual_error_response(401, "Invalid credentials", "")

    except users.DoesNotExist:
        return manual_error_response(401, "Invalid credentials", "")

def roleApi(request):
    if request.method=='GET':
        roles = role.objects.all()
        role_serializer=RoleSerializer(roles,many=True)
    try:

     return JsonResponse({'message': 'Fetched Role successfully','success':True,'respayload':role_serializer.data,},safe=False)

    except Exception as e:
        # Call the updated generate_error_response function with the exception as argument
        return generate_error_response(e)
        