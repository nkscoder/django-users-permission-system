from django.conf import settings

DEFAULT_LABEL_GROUPS = ()

DEFAULT_SKIP_PREFIXES = (
    "/",
    "/login",
    "/logout",
    "/api/",
    "/admin/",
    "/static/",
    "/media/",
    "/permissions/",
)

DEFAULT_ADMIN_ROLE_NAMES = ("admin",)

SETTING_NAME = "USER_PERMISSION_SYSTEM"


def get_ups_settings():
    return getattr(settings, SETTING_NAME, {}) or {}


def get_setting(key, default=None):
    return get_ups_settings().get(key, default)


def get_label_groups():
    groups = get_setting("LABEL_GROUPS")
    if groups is None:
        return DEFAULT_LABEL_GROUPS
    return tuple(frozenset(g) for g in groups)


def get_skip_prefixes():
    prefixes = get_setting("SKIP_PREFIXES")
    if prefixes is None:
        return DEFAULT_SKIP_PREFIXES
    return tuple(prefixes)


def get_permission_plugins():
    return list(get_setting("PLUGINS", ()))


def get_platform_adapters():
    return dict(get_setting("PLATFORM_ADAPTERS", {}))


def get_admin_role_names():
    names = get_setting("ADMIN_ROLE_NAMES")
    if names is None:
        return DEFAULT_ADMIN_ROLE_NAMES
    return tuple(names)


def get_permission_code_groups():
    """
  Optional nested permission map for templates/UI.

  Example:
      {
          "orders_create": ("orders", "create"),
          "orders_view": ("orders", "view"),
      }
  """
    return dict(get_setting("PERMISSION_CODE_GROUPS", {}))
