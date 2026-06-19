import logging
from typing import Any, Dict, List, Optional

from userspermissionsystem.models import ExternalSyncEndpoint, UserAccessControl
from userspermissionsystem.platforms.base import SyncResult
from userspermissionsystem.platforms.registry import get_platform_adapter

logger = logging.getLogger(__name__)


def get_active_endpoints(event_type: str):
    return (
        ExternalSyncEndpoint.objects.filter(
            event_type=event_type,
            is_active=True,
            app__is_active=True,
        )
        .select_related("app")
        .order_by("app__label", "id")
    )


def dispatch_sync_event(
    event_type: str,
    user,
    payload: Optional[Dict[str, Any]] = None,
    permissions: Optional[List[Any]] = None,
) -> List[SyncResult]:
    """
    Route a user lifecycle event to all configured platform adapters.
    Returns a list of SyncResult objects (one per endpoint).
    """
    payload = payload or {}
    results: List[SyncResult] = []

    if permissions is None and event_type == "access":
        access = UserAccessControl.objects.filter(user=user).first()
        if access:
            permissions = list(access.get_all_permissions())

    for endpoint in get_active_endpoints(event_type):
        adapter = get_platform_adapter(getattr(endpoint, "platform_type", "http"))
        try:
            result = adapter.sync(endpoint, event_type, user, payload, permissions)
            results.append(result)
            if result.success:
                logger.info(
                    "Sync %s → %s (%s): %s",
                    event_type,
                    endpoint.app.label,
                    adapter.platform_type,
                    result.message,
                )
            else:
                logger.warning(
                    "Sync %s → %s (%s) failed: %s",
                    event_type,
                    endpoint.app.label,
                    adapter.platform_type,
                    result.message,
                )
        except Exception as exc:
            logger.exception("Sync dispatch error for endpoint %s", endpoint.id)
            results.append(
                SyncResult(
                    success=False,
                    endpoint_id=endpoint.id,
                    platform=getattr(endpoint, "platform_type", "http"),
                    message=str(exc),
                    errors=[str(exc)],
                )
            )

    return results


def sync_user_access(user, payload: Optional[Dict[str, Any]] = None) -> List[SyncResult]:
    """Convenience wrapper for permission/access sync."""
    return dispatch_sync_event("access", user, payload=payload)
