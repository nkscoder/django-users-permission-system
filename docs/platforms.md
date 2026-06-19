# Platform Integrations

![Platform icons](images/platform-icons.png)

## HTTP (generic)

Best for custom APIs and legacy systems (e.g. SPYDER-style webhooks).

```json
{
  "platform_type": "http",
  "endpoint": "/api/register/user/",
  "auth_config": {"token": "secret", "token_type": "Bearer"},
  "extra_config": {"method": "POST", "timeout": 10}
}
```

## GitLab

| Event | Action |
|-------|--------|
| create | POST /api/v4/users |
| update | PUT /api/v4/users/:id |
| password | PUT password |
| status | block/unblock user |
| access | add group/project member |

```json
{
  "platform_type": "gitlab",
  "auth_config": {"token": "glpat-xxx", "token_type": "PRIVATE-TOKEN"},
  "extra_config": {"group_id": 42, "access_level": 30}
}
```

## GitHub

GitHub.com does not support user creation via API. This adapter syncs org and team access.

```json
{
  "platform_type": "github",
  "auth_config": {"token": "ghp_xxx"},
  "extra_config": {"org": "my-org", "team_slug": "developers", "team_role": "member"}
}
```

## Bitbucket

```json
{
  "platform_type": "bitbucket",
  "auth_config": {"token": "xxx"},
  "extra_config": {"workspace": "myteam", "permission": "member"}
}
```

## Gitea / Forgejo

Uses Gitea API v1 (GitLab-compatible patterns).

```json
{
  "platform_type": "gitea",
  "auth_config": {"token": "xxx"},
  "extra_config": {"group_id": 3}
}
```

## PyPI

Public PyPI has no user provisioning API. Use for self-hosted registries or custom token endpoints.

```json
{
  "platform_type": "pypi",
  "endpoint": "/api/v1/tokens/sync/",
  "auth_config": {"token": "xxx"},
  "extra_config": {"scopes": ["upload"]}
}
```

## Event types

| event_type | When to fire |
|------------|--------------|
| create | New user |
| update | Profile fields changed |
| password | Password changed |
| status | is_active / approval / staff flags |
| access | Roles or permissions changed |
