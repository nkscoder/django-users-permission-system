# Architecture

![Architecture diagram](images/architecture-diagram.png)

## Request flow

1. HTTP request hits `URLPermissionMiddleware`
2. First URL segment resolves to `AppModule.label` (with alias support)
3. `UserAccessControl.is_allowed(path, method, app_label)` checks permissions
4. Superusers bypass; unauthenticated users redirect to login

## Core components

| Component | File | Role |
|-----------|------|------|
| Models | models.py | AppModule, permissions, roles, sync endpoints |
| Middleware | middleware.py | Enforce URL access |
| URL matching | url_permissions.py | Label aliases, path patterns |
| Sync dispatcher | sync.py | Route events to platform adapters |
| Plugins | plugins/ | Optional per-project extensions |
| Platforms | platforms/ | GitLab, GitHub, PyPI, etc. |

## Sync flow

```
User signal → dispatch_sync_event()
           → ExternalSyncEndpoint (DB)
           → Platform adapter (GitLab/GitHub/HTTP...)
           → External API
```

## Extensibility

- **Settings**: `LABEL_GROUPS`, `SKIP_PREFIXES`, `PLUGINS`
- **Database**: `AppModuleAlias` for runtime label mapping
- **Code**: subclass `PermissionPlugin` or `PlatformAdapter`

## Data model relationships

```
AppModule
  ├── AppURLPermission (many)
  ├── ExternalSyncEndpoint (many)
  └── AppModuleAlias (many)

Role ──M2M── AppURLPermission
UserAccessControl ──M2M── Role
UserAccessControl ──M2M── AppURLPermission
UserAccessControl ──1:1── User (AUTH_USER_MODEL)
```
