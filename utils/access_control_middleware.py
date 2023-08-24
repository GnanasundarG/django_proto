from django.conf import settings
from django.http import HttpResponseForbidden
from acl.models import api_url_access, api_url
from login.models import role, users
from login.serializers import RoleSerializer
from acl.serializers import ApiUrlSerializer, ApiUrlAccessSerializer
from login.response_utils import generate_error_response, manual_error_response


# class AccessControlMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # Implement your access control logic here based on the user's role and API.
#         # if not request.user.is_authenticated:
#         #     return HttpResponseForbidden("Access forbidden. Please log in.")

#         # Extract the JWT token from the request header
#         # jwt_token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]

#         # Decode the JWT token using the secret key from settings
#         # decoded_token = jwt.decode(
#         #     jwt_token, settings.SECRET_KEY, algorithms=['HS256'])

#         # Access the user's role from the payload
#         # user_role = decoded_token.get('role')

#         # Retrieve the user's role from the database.
#         try:
#             user_role = Role.objects.get(name='PT')
#         except Role.DoesNotExist:
#             return HttpResponseForbidden("Access forbidden. Role not found.")
#         except user_role.role != 'PT':
#             return HttpResponseForbidden("Access forbidden for your role")

#         # Define a mapping of role and the APIs it can access.
#         # role_apis = user_role.apis.all()
#         # allowed_api_paths = [api.path for api in role_apis]

#         # Get the current API path being requested.
#         # current_api_path = request.path

#         # Check if the user's role has permission to access the requested API.
#         # if current_api_path not in allowed_api_paths:
#         #     return HttpResponseForbidden("Access forbidden. Insufficient role permissions.")

#         # If access is granted, simply return None and allow the request to proceed.
#         return None



class AccessControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Implement your access control logic here based on the user's role and API.
        # if not request.user.is_authenticated:
        #     return HttpResponseForbidden("Access forbidden. Please log in.")

        # Retrieve the user's role from the database.
        # try:
        #    user_role = role.objects.get(role_code='PT')
        #     # user_role = request.user.role  # Assuming a ForeignKey field named "role" in the "users" model
        # except users.DoesNotExist:
        #     return HttpResponseForbidden("Access forbidden. Role not found.")

        # # Check if the user's role has permission to access the current API endpoint and method.
        try:
            # getting data from request and JWT
            current_url = request.path 
            method = request.method.lower()
            user_role = "PT"

            excluded_url = ["/api/login", "/api/role"]

            if current_url in excluded_url:
                return self.get_response(request)
            else:
                # getting role data
                role_data = role.objects.get(role_code = user_role)
                role_id = RoleSerializer(role_data).data['id_role']

                # getting url data
                url_data = api_url.objects.get(api_url = current_url)
                url_id = ApiUrlSerializer(url_data).data['id_api_url']

                # getting url access data
                url_access_data = api_url_access.objects.get(role_id = role_id, url_id = url_id)
                url_access_serialized_data = ApiUrlAccessSerializer(url_access_data).data

                # checking whether user is allowed to access the API
                if url_access_serialized_data[method] == True:
                    return self.get_response(request)
                else:
                    return generate_error_response(
                        Exception("Access denied"),
                        code = 403,
                        type="Access Error",
                    )

        except role.DoesNotExist:
            return generate_error_response(
                Exception("Role doesn't have access"),
                code = 403,
                type="Access Error",
            )
            
        except api_url.DoesNotExist:
            return generate_error_response(
                Exception("URL has no defined access"),
                code = 403,
                type="Access Error",
            )

        except api_url_access.DoesNotExist:
            return generate_error_response(
                Exception("URL has no defined access"),
                code = 403,
                type="Access Error",
            )
        
        except Exception as e:
            return generate_error_response(
                Exception(e.message),
                ode = 403,
                type="Access Error",
            )
        # try:
        #     acl_entry = api_url_access.objects.filter(url__api_url=current_url, role=user_role)
        # except api_url_access.DoesNotExist:
        #     return HttpResponseForbidden("Access forbidden. Insufficient permissions.")
        
        # # Check if the user has the required permission for the requested method.
        # if method == 'get' and not acl_entry.get:
        #     return HttpResponseForbidden("Access forbidden. Insufficient permissions for GET method.")
        # elif method == 'post' and not acl_entry.post:
        #     return HttpResponseForbidden("Access forbidden. Insufficient permissions for POST method.")
        # elif method == 'patch' and not acl_entry.patch:
        #     return HttpResponseForbidden("Access forbidden. Insufficient permissions for PATCH method.")
        # elif method == 'delete' and not acl_entry.delete:
        #     return HttpResponseForbidden("Access forbidden. Insufficient permissions for DELETE method.")

        # If access is granted, simply return None and allow the request to proceed.
