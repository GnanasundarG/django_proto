import functools
import mimetypes
import xlrd
from django.http import JsonResponse

from utils.response_utils import manual_error_response

def validate_schedule_upload(view_func):
    @functools.wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if scheduletypeid exists in the query parameters
        scheduletypeid = request.GET.get('scheduletypeid')
        if not scheduletypeid:
            return manual_error_response(400, 'scheduletypeid is missing in the query parameters', "")

        # Check if the request contains a file upload
        if 'file' not in request.FILES:
            return manual_error_response(400, 'XL file is not uploaded', "")

        # Check if the uploaded file is in the Excel (XL) format
        file = request.FILES['file']
        content_type, encoding = mimetypes.guess_type(file.name)
        if content_type != 'application/vnd.ms-excel':
            return manual_error_response(400, 'Invalid file format. Expected an Excel (XL) file.', "")

        # Additional validation checks can be added here, e.g., file size, file structure, etc.

        return view_func(request, *args, **kwargs)
    return _wrapped_view

# def validate_schedule_upload(view_func):
#     @functools.wraps(view_func)
#     def _wrapped_view(request, *args, **kwargs):
#         # Check if scheduletypeid exists in the query parameters
#         scheduletypeid = request.GET.get('scheduletypeid')
#         if not scheduletypeid:
#             return manual_error_response(400, 'scheduletypeid is missing in the query parameters', "")

#         # Check if the request contains a file upload
#         if 'file' not in request.FILES:
#             return manual_error_response(400, 'XL file is not uploaded', "")

#         # Check if the uploaded file is in the Excel (XL) format
#         file = request.FILES['file']
#         content_type, encoding = mimetypes.guess_type(file.name)
#         if content_type != 'application/vnd.ms-excel':
#             return manual_error_response(400, 'Invalid file format. Expected an Excel (XL) file.', "")

#         # Additional validation checks can be added here, e.g., file size, file structure, etc.

#         return view_func(request, *args, **kwargs)

#     return _wrapped_view
