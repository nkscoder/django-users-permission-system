import logging
from typing import Any, Dict, List, Optional

import requests

from userspermissionsystem.platforms.base import PlatformAdapter, SyncResult

logger = logging.getLogger(__name__)


class BitbucketAdapter(PlatformAdapter):
    """Bitbucket Cloud user and workspace access sync."""

    platform_type = "bitbucket"

    def sync(
        self,
        endpoint,
        event_type: str,
        user,
        payload: Dict[str, Any],
        permissions: Optional[List[Any]] = None,
    ) -> SyncResult:
        auth_config = getattr(endpoint, "auth_config", None) or {}
        extra_config = getattr(endpoint, "extra_config", None) or {}
        base_url = (endpoint.app.base_url or "https://api.bitbucket.org/2.0").rstrip("/")
        headers = self._auth_headers(auth_config)
        timeout = int(extra_config.get("timeout", 15))
        username = self._username(user, payload)

        try:
            if event_type in ("create", "update"):
                return self._invite_user(
                    base_url, headers, timeout, payload, extra_config, endpoint
                )
            if event_type == "access":
                return self._sync_workspace_access(
                    base_url, headers, timeout, username, extra_config, endpoint
                )
            if event_type == "password":
                return SyncResult(
                    success=False,
                    endpoint_id=endpoint.id,
                    platform=self.platform_type,
                    message="Bitbucket password sync is not supported via API",
                )
            if event_type == "status":
                return self._deactivate_user(
                    base_url, headers, timeout, username, payload, extra_config, endpoint
                )
            return SyncResult(
                success=False,
                endpoint_id=endpoint.id,
                platform=self.platform_type,
                message=f"Unsupported event type: {event_type}",
            )
        except Exception as exc:
            logger.exception("Bitbucket sync failed")
            return SyncResult(
                success=False,
                endpoint_id=endpoint.id,
                platform=self.platform_type,
                message=str(exc),
                errors=[str(exc)],
            )

    def _invite_user(self, base_url, headers, timeout, payload, extra_config, endpoint):
        workspace = extra_config.get("workspace")
        if not workspace:
            return SyncResult(
                success=False,
                endpoint_id=endpoint.id,
                platform=self.platform_type,
                message="extra_config.workspace is required",
            )
        email = payload.get("email")
        if not email:
            return SyncResult(
                success=False,
                endpoint_id=endpoint.id,
                platform=self.platform_type,
                message="email is required for Bitbucket invitations",
            )
        url = f"{base_url}/workspaces/{workspace}/permissions"
        body = {
            "email": email,
            "permission": extra_config.get("permission", "member"),
        }
        response = requests.put(url, json=body, headers=headers, timeout=timeout)
        ok = response.status_code in (200, 201, 204)
        return SyncResult(
            success=ok,
            endpoint_id=endpoint.id,
            platform=self.platform_type,
            message="invitation sent" if ok else response.text[:500],
            status_code=response.status_code,
            response_body=response.text[:2000],
        )

    def _sync_workspace_access(
        self, base_url, headers, timeout, username, extra_config, endpoint
    ):
        workspace = extra_config.get("workspace")
        if not workspace:
            return SyncResult(
                success=False,
                endpoint_id=endpoint.id,
                platform=self.platform_type,
                message="extra_config.workspace is required",
            )
        url = f"{base_url}/workspaces/{workspace}/permissions"
        body = {
            "user": {"type": "user", "username": username},
            "permission": extra_config.get("permission", "member"),
        }
        response = requests.put(url, json=body, headers=headers, timeout=timeout)
        ok = response.status_code in (200, 201, 204)
        return SyncResult(
            success=ok,
            endpoint_id=endpoint.id,
            platform=self.platform_type,
            message="workspace access synced" if ok else response.text[:500],
            status_code=response.status_code,
            response_body=response.text[:2000],
        )

    def _deactivate_user(
        self, base_url, headers, timeout, username, payload, extra_config, endpoint
    ):
        if payload.get("is_approved", True):
            return SyncResult(
                success=True,
                endpoint_id=endpoint.id,
                platform=self.platform_type,
                message="user remains active; no Bitbucket action needed",
            )
        workspace = extra_config.get("workspace")
        if not workspace:
            return SyncResult(
                success=False,
                endpoint_id=endpoint.id,
                platform=self.platform_type,
                message="extra_config.workspace is required",
            )
        url = f"{base_url}/workspaces/{workspace}/members/{username}"
        response = requests.delete(url, headers=headers, timeout=timeout)
        ok = response.status_code in (200, 204)
        return SyncResult(
            success=ok,
            endpoint_id=endpoint.id,
            platform=self.platform_type,
            message="user removed from workspace" if ok else response.text[:500],
            status_code=response.status_code,
            response_body=response.text[:2000],
        )
