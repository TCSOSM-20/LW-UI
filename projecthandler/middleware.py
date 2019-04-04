from authosm.exceptions import OSMAuthException
from django.shortcuts import render
import json

class OsmProjectMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        return None

    def process_exception(self, request, exception):
        if isinstance(exception, OSMAuthException):            
            try:
                error_message = exception.message['detail']
            except Exception as e:
                print e
                error_message = 'Unknown error'
            return render(request, 'error.html', {'error_message': error_message, 'collapsed_sidebar': False})