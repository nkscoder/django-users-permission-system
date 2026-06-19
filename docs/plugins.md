# Plugins

## Permission plugins

Register in settings:

```python
USER_PERMISSION_SYSTEM = {
    "PLUGINS": [
        "myapp.permissions.TicketsPermissionPlugin",
    ],
}
```

Example:

```python
from userspermissionsystem.plugins.base import PermissionPlugin

class TicketsPermissionPlugin(PermissionPlugin):
    label = "tickets"

    def get_label_aliases(self):
        return {"tickets", "ticket"}
```

Plugins can:

- Define label aliases for URL routing
- Expose custom permission code mappings
- Add optional `check_permission()` logic

## Platform adapters

Register custom sync targets:

```python
USER_PERMISSION_SYSTEM = {
    "PLATFORM_ADAPTERS": {
        "jira": "myapp.sync.JiraAdapter",
    },
}
```

Example:

```python
from userspermissionsystem.platforms.base import PlatformAdapter, SyncResult

class JiraAdapter(PlatformAdapter):
    platform_type = "jira"

    def sync(self, endpoint, event_type, user, payload, permissions=None):
        # call Jira API
        return SyncResult(success=True, platform="jira", message="synced")
```

Or register at runtime:

```python
from userspermissionsystem.platforms.registry import register_platform_adapter
register_platform_adapter(JiraAdapter())
```

## App module aliases (database)

Instead of code, add rows in `AppModuleAlias`:

- module → FIU AppModule
- alias → `str`

This maps `/str/...` URLs to FIU permissions.
