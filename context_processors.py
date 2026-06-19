from userspermissionsystem.conf import get_admin_role_names
from userspermissionsystem.models import AppModule
from userspermissionsystem.role_permissions import get_user_roles, user_is_privileged


def base_context(request):
    context = {"current_module": None}
    try:
        path_prefix = request.path_info.lstrip("/").split("/")[0]
        if path_prefix:
            context["current_module"] = AppModule.objects.filter(
                label=path_prefix, is_active=True
            ).first()
    except Exception:
        pass
    return context


def user_roles_context(request):
    context = {
        "is_admin_role": False,
        "user_role_names": [],
        "privileged_role_names": list(get_admin_role_names()),
    }

    if request.user.is_authenticated and hasattr(request.user, "url_access"):
        context["user_role_names"] = get_user_roles(request.user)
        context["is_admin_role"] = user_is_privileged(request.user)

    return context
