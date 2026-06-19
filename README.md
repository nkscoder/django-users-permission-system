# django-users-permission-system

[![PyPI version](https://badge.fury.io/py/django-users-permission-system.svg)](https://pypi.org/project/django-users-permission-system/)
[![Python versions](https://img.shields.io/pypi/pyversions/django-users-permission-system.svg)](https://pypi.org/project/django-users-permission-system/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Django](https://img.shields.io/badge/Django-4.2%2B-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![GitHub Repo](https://img.shields.io/github/stars/nkscoder/django-users-permission-system?style=social)](https://github.com/nkscoder/django-users-permission-system)

**Generic Django RBAC plugin** for URL-based permissions, role management, module menus, and multi-platform user sync (GitLab, GitHub, Bitbucket, Gitea, PyPI).

Install from [PyPI](https://pypi.org/project/django-users-permission-system/):

```bash
pip install django-users-permission-system
```

Use in **any Django project** as a drop-in app — no hardcoded project dependencies.

![Architecture](docs/images/architecture-diagram.png)

## Why use this package?

- **URL-level RBAC** — enforce permissions per route and HTTP method
- **Role + direct grants** — flexible `Role` and `UserAccessControl` models
- **Module registry** — database-driven app modules and home menu
- **Platform sync** — push user create/update/password/access to external APIs
- **Pluggable** — custom permission plugins and platform adapters via settings
- **AI dashboard** — built-in admin dashboard, docs browser, and setup assistant

## Features

- URL permission middleware for Django
- Database-driven module registry (`AppModule`)
- Roles + direct user permissions (`Role`, `UserAccessControl`)
- Generic role API (`user_has_role`, `user_has_permission_code`, etc.)
- Pluggable permission modules via settings
- Multi-platform outbound sync (`ExternalSyncEndpoint`)
- Configurable label aliases (settings, DB, or plugins)
- AI Dashboard with stats, platform overview, and setup assistant
- Full documentation with architecture and platform guides

## Quick start

```bash
pip install django-users-permission-system
```

```python
# settings.py
INSTALLED_APPS += [
    "import_export",
    "userspermissionsystem.apps.UserspermissionsystemConfig",
]

MIDDLEWARE += [
    "userspermissionsystem.middleware.URLPermissionMiddleware",
]
```

```bash
python manage.py migrate userspermissionsystem
```

## AI Dashboard & Documentation

```python
# urls.py
path("permissions/", include("userspermissionsystem.urls")),
```

| Page | URL |
|------|-----|
| AI Dashboard | `/permissions/dashboard/` |
| Documentation | `/permissions/docs/` |
| AI Assistant API | `/permissions/api/ai-assistant/` |

![Dashboard](docs/images/dashboard-hero.png)

![Platforms](docs/images/platform-icons.png)

## Django settings

```python
USER_PERMISSION_SYSTEM = {
    "SKIP_PREFIXES": ["/", "/login", "/logout", "/api/", "/admin/", "/static/", "/media/", "/permissions/"],
    "LABEL_GROUPS": [["orders", "order"]],
    "ADMIN_ROLE_NAMES": ["admin"],
    "PLUGINS": [],
    "PLATFORM_ADAPTERS": {},
    "PERMISSION_CODE_GROUPS": {
        "orders_create": ("orders", "create"),
        "orders_view": ("orders", "view"),
    },
}
```

## Generic role permissions

```python
from userspermissionsystem.role_permissions import (
    user_has_permission_code,
    user_has_url_permission,
    user_has_module_access,
    user_has_role,
    user_is_privileged,
    get_grouped_permissions,
)
```

See [docs/roles.md](docs/roles.md) for the full API.

## Platform integrations

| Platform | `platform_type` |
|----------|-----------------|
| Generic HTTP | `http` |
| GitLab | `gitlab` |
| GitHub | `github` |
| Bitbucket | `bitbucket` |
| Gitea / Forgejo | `gitea` |
| PyPI / registry webhooks | `pypi` |

See [docs/platforms.md](docs/platforms.md) for configuration examples.

## Documentation

| Guide | Description |
|-------|-------------|
| [index.md](docs/index.md) | Overview |
| [installation.md](docs/installation.md) | Setup |
| [architecture.md](docs/architecture.md) | System design |
| [roles.md](docs/roles.md) | Role & permission API |
| [platforms.md](docs/platforms.md) | GitLab, GitHub, PyPI |
| [plugins.md](docs/plugins.md) | Custom plugins |
| [api.md](docs/api.md) | API reference |

## Links

- **PyPI:** https://pypi.org/project/django-users-permission-system/
- **GitHub:** https://github.com/nkscoder/django-users-permission-system
- **Issues:** https://github.com/nkscoder/django-users-permission-system/issues

## Keywords

`django` `rbac` `permissions` `role-based-access-control` `authorization` `middleware` `gitlab` `github` `user-sync` `django-plugin` `access-control` `url-permissions`

## License

This project is licensed under the [MIT License](LICENSE).

Copyright (c) 2026 [Nitesh (nkscoder)](https://github.com/nkscoder)
