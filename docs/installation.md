# Installation Guide

## 1. Install package

```bash
pip install django-users-permission-system
# or from source
pip install -e .
```

## 2. Django settings

```python
INSTALLED_APPS = [
    # ...
    "import_export",
    "userspermissionsystem.apps.UserspermissionsystemConfig",
]

MIDDLEWARE = [
    # ...
    "userspermissionsystem.middleware.URLPermissionMiddleware",
]

ROOT_URLCONF = "myproject.urls"

USER_PERMISSION_SYSTEM = {
    "SKIP_PREFIXES": [
        "/", "/login", "/logout", "/api/", "/admin/", "/static/", "/media/",
        "/permissions/",
    ],
    "LABEL_GROUPS": [
        ["reports", "report_management_system"],
        ["tickets", "ticket"],
    ],
    "PLUGINS": [],
    "PLATFORM_ADAPTERS": {},
}
```

## 3. URL configuration

```python
# myproject/urls.py
from django.urls import include, path

urlpatterns = [
    path("permissions/", include("userspermissionsystem.urls")),
    path("admin/", admin.site.urls),
]
```

## 4. Migrate

```bash
python manage.py migrate userspermissionsystem
```

## 5. Create first module

In Django Admin:

1. Add `AppModule` (label must match first URL segment)
2. Add `AppURLPermission` rows (url, method, code)
3. Create `Role` and assign permissions
4. Assign `UserAccessControl` to users

## 6. Optional platform sync

1. Set `AppModule.base_url` for external system
2. Add `ExternalSyncEndpoint` with `platform_type`
3. Wire signals:

```python
from userspermissionsystem.sync import dispatch_sync_event

dispatch_sync_event("create", user, {"username": user.username, "email": user.email})
```

## 7. Open AI dashboard

Visit `/permissions/dashboard/` as a staff user.
