# Role & Permission API

Generic helpers live in `userspermissionsystem.role_permissions`.

## Check by permission code

```python
from userspermissionsystem.role_permissions import user_has_permission_code

if user_has_permission_code(request.user, "orders_create", app_label="orders"):
    ...
```

## Check by URL + method

```python
from userspermissionsystem.role_permissions import user_has_url_permission

if user_has_url_permission(request.user, "/orders/create/", "POST", app_label="orders"):
    ...
```

## Check module access

```python
from userspermissionsystem.role_permissions import user_has_module_access

if user_has_module_access(request.user, "orders"):
    ...
```

## Check roles

```python
from userspermissionsystem.role_permissions import user_has_role, user_is_privileged

if user_has_role(request.user, "editor"):
    ...

if user_is_privileged(request.user):  # uses ADMIN_ROLE_NAMES setting
    ...
```

## Grouped UI permissions

Configure in settings:

```python
USER_PERMISSION_SYSTEM = {
    "PERMISSION_CODE_GROUPS": {
        "orders_create": ("orders", "create"),
        "orders_view": ("orders", "view"),
    },
}
```

```python
from userspermissionsystem.role_permissions import get_grouped_permissions

permissions = get_grouped_permissions(request.user)
# {"orders": {"create": True, "view": False}}
```

## UserAccessControl instance methods

```python
access = request.user.url_access
access.has_role("editor")
access.has_code("orders_create", app_label="orders")
access.has_module_access("orders")
access.get_permission_codes()
access.get_role_names()
```

## Settings

```python
USER_PERMISSION_SYSTEM = {
    "ADMIN_ROLE_NAMES": ["admin", "supervisor"],
    "LABEL_GROUPS": [["orders", "order"]],
    "PERMISSION_CODE_GROUPS": {},
}
```

No hardcoded app names (tickets, fiu, reports, etc.) are required in the core package.
