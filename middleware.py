# from django.http import HttpResponseForbidden
# from django.shortcuts import redirect
# from django.utils.deprecation import MiddlewareMixin

# class URLPermissionMiddleware(MiddlewareMixin):
#     def process_view(self, request, view_func, view_args, view_kwargs):
#         path = request.path
#         method = request.method

#         # Allow superusers full access
#         if request.user.is_authenticated and request.user.is_superuser:
#             return None

#         # Redirect unauthenticated users
#         if not request.user.is_authenticated:
#             return redirect('login')  # Or use HttpResponseForbidden()

#         # Check if user has access via UserAccessControl
#         acl = getattr(request.user, 'url_access', None)
#         if acl and acl.is_allowed(path, method):
#             return None

#         return HttpResponseForbidden("You do not have permission to access this URL.")

from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from userspermissionsystem.conf import get_skip_prefixes
from userspermissionsystem.models import AppModule
from userspermissionsystem.url_permissions import app_labels_compatible

# class URLPermissionMiddleware(MiddlewareMixin):
#     # Define paths to skip permission check (API, Admin, Static, etc.)
#     SKIP_PREFIXES = [
#         '/',             # home page
#         '/login',        # login view
#         '/logout',  
#         '/api/',         # Django REST Framework or custom APIs
#         '/admin/',       # Admin interface
#         '/static/',      # Static files
#         '/media/',       # Media files
#     ]

#     def should_skip(self, path):
#         return any(path.startswith(prefix) for prefix in self.SKIP_PREFIXES)

#     def process_view(self, request, view_func, view_args, view_kwargs):
#         path = request.path
#         method = request.method

#         # Skip if request path is in excluded prefixes
#         if self.should_skip(path):
#             return None

#         # Allow superusers full access
#         if request.user.is_authenticated and request.user.is_superuser:
#             return None

#         # Redirect unauthenticated users
#         if not request.user.is_authenticated:
#             return redirect('login')  # Or: return HttpResponseForbidden()

#         # Check user access via model
#         acl = getattr(request.user, 'url_access', None)
#         if acl and acl.is_allowed(path, method):
#             return None

#         return HttpResponseForbidden("You do not have permission to access this URL.")
class URLPermissionMiddleware(MiddlewareMixin):
    def get_skip_prefixes(self):
        return get_skip_prefixes()

    def should_skip(self, path):
        return any(path.startswith(prefix) for prefix in self.get_skip_prefixes())

    def get_app_label_from_path(self, path):
        """Extracts the first URL segment to match against AppModule.label"""
        parts = path.lstrip('/').split('/')
        return parts[0] if parts else None

    def resolve_app_module(self, label):
        if not label:
            return None
        try:
            return AppModule.objects.get(label=label, is_active=True)
        except AppModule.DoesNotExist:
            for module in AppModule.objects.filter(is_active=True):
                if app_labels_compatible(label, module.label):
                    return module
            return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        path = request.path
        method = request.method

        if self.should_skip(path):
            return None

        if not request.user.is_authenticated:
            return redirect('login')

        if request.user.is_superuser:
            return None

        # Get app label from URL path
        label = self.get_app_label_from_path(path)
        app_module = self.resolve_app_module(label)
        if not app_module:
            print("Access denied: unknown module")
            return HttpResponseForbidden("Access denied: unknown module.")
        request.app_module = app_module

        # Check permission scoped to this app only (avoids cross-app URL collisions).
        acl = getattr(request.user, 'url_access', None)
        if acl and acl.is_allowed(path, method, app_label=label):
            return None

        return HttpResponseForbidden("You do not have permission to access this URL.")