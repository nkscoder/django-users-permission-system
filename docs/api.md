# API Reference

## Views / helpers

### get_module_access(request)

Returns `AppModule` queryset visible on home menu for current user.

### get_api_urls(event_type)

Legacy: returns HTTP endpoint URLs only.

### sync_user_event(event_type, user, payload)

Preferred sync entry point (wraps dispatcher).

## Sync

### dispatch_sync_event(event_type, user, payload=None, permissions=None)

Dispatches to all active `ExternalSyncEndpoint` rows for the event.

Returns: `list[SyncResult]`

### sync_user_access(user, payload=None)

Shortcut for `event_type="access"`.

## Permission checks

### UserAccessControl.is_allowed(url, method, app_label=None)

Core RBAC check used by middleware.

### app_labels_compatible(request_label, perm_label)

Returns True when labels belong to same module (aliases, plugins, settings).

## Dashboard

| URL | View | Access |
|-----|------|--------|
| /permissions/dashboard/ | AI dashboard | staff |
| /permissions/docs/ | Documentation browser | staff |
| /permissions/api/ai-assistant/ | AI assistant POST API | staff |

## AI assistant POST

```bash
curl -X POST /permissions/api/ai-assistant/ \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I configure GitLab sync?"}'
```

Response:

```json
{"answer": "Create an AppModule with base_url=..."}
```

## SyncResult fields

- success (bool)
- endpoint_id
- platform
- message
- status_code
- response_body
- errors
