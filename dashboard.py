"""Dashboard stats and AI assistant helpers."""

from django.db.models import Count

from userspermissionsystem.models import (
    AppModule,
    AppURLPermission,
    ExternalSyncEndpoint,
    Role,
    UserAccessControl,
)
from userspermissionsystem.platforms.registry import get_registered_platforms


def get_dashboard_stats():
    modules = AppModule.objects.annotate(
        permission_count=Count("permissions", distinct=True),
        endpoint_count=Count("sync_endpoints", distinct=True),
    ).order_by("name")

    platform_counts = {}
    for ep in ExternalSyncEndpoint.objects.filter(is_active=True).select_related("app"):
        key = ep.platform_type or "http"
        platform_counts[key] = platform_counts.get(key, 0) + 1

    return {
        "module_count": AppModule.objects.filter(is_active=True).count(),
        "permission_count": AppURLPermission.objects.filter(is_active=True).count(),
        "role_count": Role.objects.filter(is_active=True).count(),
        "user_access_count": UserAccessControl.objects.count(),
        "sync_endpoint_count": ExternalSyncEndpoint.objects.filter(is_active=True).count(),
        "modules": modules,
        "platform_counts": platform_counts,
        "registered_platforms": get_registered_platforms(),
    }


AI_KNOWLEDGE = [
    {
        "keywords": ["install", "setup", "pip", "integrate"],
        "answer": (
            "Add `userspermissionsystem` to INSTALLED_APPS, run migrations, add "
            "URLPermissionMiddleware, and configure USER_PERMISSION_SYSTEM in settings. "
            "See docs/installation.md for the full checklist."
        ),
    },
    {
        "keywords": ["gitlab", "git lab"],
        "answer": (
            "Create an AppModule with base_url=https://gitlab.example.com, then add "
            "ExternalSyncEndpoint rows with platform_type=gitlab. Set auth_config "
            '{"token": "glpat-...", "token_type": "PRIVATE-TOKEN"} and extra_config '
            '{"group_id": 12, "access_level": 30} for access sync.'
        ),
    },
    {
        "keywords": ["github", "git hub", "org", "team"],
        "answer": (
            "GitHub adapter manages org membership and team access. Use platform_type=github, "
            'auth_config {"token": "ghp_..."}, extra_config '
            '{"org": "my-org", "team_slug": "developers"}.'
        ),
    },
    {
        "keywords": ["pypi", "package", "registry", "token"],
        "answer": (
            "PyPI public registry has no user-provisioning API. Use platform_type=pypi for "
            "self-hosted registries or custom token webhooks. Configure token_endpoint in extra_config."
        ),
    },
    {
        "keywords": ["plugin", "extend", "custom adapter"],
        "answer": (
            "Register permission plugins via USER_PERMISSION_SYSTEM['PLUGINS'] and platform "
            "adapters via PLATFORM_ADAPTERS. Subclass PermissionPlugin or PlatformAdapter."
        ),
    },
    {
        "keywords": ["middleware", "url", "permission", "403", "denied"],
        "answer": (
            "URLPermissionMiddleware maps the first URL segment to AppModule.label, then checks "
            "UserAccessControl.is_allowed(). Add paths to SKIP_PREFIXES to bypass checks."
        ),
    },
    {
        "keywords": ["sync", "webhook", "create user", "password"],
        "answer": (
            "Call dispatch_sync_event('create', user, payload) from your user signals. "
            "Supported events: create, update, password, status, access."
        ),
    },
    {
        "keywords": ["role", "rbac", "access control"],
        "answer": (
            "Assign roles and direct AppURLPermission rows via UserAccessControl. "
            "Roles bundle permissions; users inherit both role and direct grants."
        ),
    },
]


def ai_assistant_reply(question: str) -> str:
    text = (question or "").strip().lower()
    if not text:
        return "Ask me about installation, platforms (GitLab, GitHub, PyPI), plugins, middleware, or sync."

    best_score = 0
    best_answer = None
    for item in AI_KNOWLEDGE:
        score = sum(1 for kw in item["keywords"] if kw in text)
        if score > best_score:
            best_score = score
            best_answer = item["answer"]

    if best_answer:
        return best_answer

    return (
        "I can help with setup, RBAC, middleware, platform sync (GitLab, GitHub, Bitbucket, "
        "Gitea, PyPI, HTTP), and writing custom plugins. Try: 'How do I configure GitLab sync?'"
    )
