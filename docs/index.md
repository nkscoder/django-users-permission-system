# Users Permission System

Django plugin for URL-based RBAC, module menus, and multi-platform user sync.

![Architecture](images/architecture-diagram.png)

## What you get

- Middleware-enforced URL permissions
- Database module registry (`AppModule`)
- Roles + direct grants (`UserAccessControl`)
- Platform sync: HTTP, GitLab, GitHub, Bitbucket, Gitea, PyPI
- AI dashboard for setup help and health overview

## Quick links

- Installation → installation.md
- Architecture → architecture.md
- Platforms → platforms.md
- Plugins → plugins.md
- API reference → api.md

## Dashboard

After install, mount URLs and open:

```
/permissions/dashboard/
/permissions/docs/
```

Staff users can view stats, platform status, architecture diagrams, and use the AI assistant.

## Supported platforms

![Platforms](images/platform-icons.png)

| Platform | Use case |
|----------|----------|
| HTTP | Generic REST webhooks |
| GitLab | User + group/project access |
| GitHub | Org + team membership |
| Bitbucket | Workspace invites |
| Gitea | Self-hosted git (GitLab-like API) |
| PyPI | Token / registry webhooks |

## License

MIT
