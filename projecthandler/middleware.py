
class OsmProjectMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        return None