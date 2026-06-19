import warnings

from userspermissionsystem.models import ExternalSyncEndpoint
from userspermissionsystem.role_permissions import (
    get_allowed_modules_for_user,
    get_grouped_permissions,
    get_user_permission_codes,
    normalize_permission_key,
    user_has_module_access,
    user_has_permission_code,
    user_has_url_permission,
)
from userspermissionsystem.sync import dispatch_sync_event

__all__ = [
    "get_module_access",
    "get_api_urls",
    "sync_user_event",
    "user_has_url_permission",
    "user_has_permission_code",
    "user_has_module_access",
    "get_user_permission_codes",
    "get_grouped_permissions",
    "normalize_permission_key",
]


def get_module_access(request):
    try:
        return list(get_allowed_modules_for_user(request.user))
    except Exception:
        return []


def get_api_urls(event_type: str) -> list[str]:
    urls = []
    try:
        endpoints = ExternalSyncEndpoint.objects.filter(
            event_type=event_type,
            is_active=True,
            app__is_active=True,
        ).select_related("app")
        for ep in endpoints:
            if getattr(ep, "platform_type", "http") not in ("http", "pypi", "custom"):
                continue
            if not ep.endpoint:
                continue
            try:
                urls.append(ep.app.get_api_url(ep.endpoint))
            except Exception:
                continue
    except Exception:
        pass
    return urls


def sync_user_event(event_type: str, user, payload=None):
    return dispatch_sync_event(event_type, user, payload=payload or {})


def _deprecated(name, replacement):
    warnings.warn(
        f"{name} is deprecated. Use {replacement} from userspermissionsystem.role_permissions.",
        DeprecationWarning,
        stacklevel=2,
    )


def can_create_ticket(user):
    _deprecated("can_create_ticket", "user_has_url_permission(user, url, method, app_label)")
    return user_has_url_permission(user, "/create_ticket/", "POST", app_label="tickets")


def can_ticket_list(user):
    _deprecated("can_ticket_list", "user_has_url_permission(user, url, method, app_label)")
    return user_has_url_permission(user, "/ticket_list/", "GET", app_label="tickets")


def can_map_view(user):
    _deprecated("can_map_view", "user_has_permission_code(user, code)")
    return user_has_permission_code(user, "map_view")


def get_mapping_permissions(user):
    _deprecated("get_mapping_permissions", "get_grouped_permissions(user)")
    return get_grouped_permissions(user)


def user_has_ticket_access(user):
    _deprecated("user_has_ticket_access", "user_has_module_access(user, module_label)")
    return user_has_module_access(user, "tickets")
