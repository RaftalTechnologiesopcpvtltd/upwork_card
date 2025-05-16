from django.http import HttpResponseForbidden

class AdminPanelAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/adminpanel/'):
            if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
                return HttpResponseForbidden("<h2 style='color:red;'>You are not authorized to access the admin panel.</h2>")
        return self.get_response(request)
