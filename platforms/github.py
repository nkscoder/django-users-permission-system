import logging
from typing import Any, Dict, List, Optional

import requests

from userspermissionsystem.platforms.base import PlatformAdapter, SyncResult

logger = logging.getLogger(__name__)


class GitHubAdapter(PlatformAdapter):
    """
    GitHub org/team sync. Public GitHub.com does not support user creation;
    this adapter manages org membership and team access for existing users.
    """

    platform_type = "github"

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
        base_url = (endpoint.app.base_url or "https://api.github.com").rstrip("/")
        headers = self._auth_headers(auth_config)
        headers.setdefault("Accept", "application/vnd.github+json")
        headers.setdefault("X-GitHub-Api-Version", "2022-11-28")
        timeout = int(extra_config.get("timeout", 15))
        username = self._username(user, payload)

        try:
            if event_type in ("create", "update", "status"):
                return self._ensure_org_membership(
                    base_url, headers, timeout, username, extra_config, endpoint
                )
            if event_type == "access":
                return self._sync_team_access(
                    base_url, headers, timeout, username, extra_config, endpoint
                )
            if event_type == "password":
                return SyncResult(
                    success=False,
                    endpoint_id=endpoint.id,
                    platform=self.platform_type,
                    message="GitHub password sync is not supported via API",
                )
            return SyncResult(
                success=False,
                endpoint_id=endpoint.id,
                platform=self.platform_type,
                message=f"Unsupported event type: {event_type}",
            )
        except Exception as exc:
            logger.exception("GitHub sync failed")
            return SyncResult(
                success=False,
                endpoint_id=endpoint.id,
                platform=self.platform_type,
                message=str(exc),
                errors=[str(exc)],
            )

    def _ensure_org_membership(
        self, base_url, headers, timeout, username, extra_config, endpoint
    ):
        org = extra_config.get("org")
        if not org:
            return SyncResult(
                success=False,
                endpoint_id=endpoint.id,
                platform=self.platform_type,
                message="extra_config.org is required for GitHub sync",
            )

        role = extra_config.get("role", "member")
        url = f"{base_url}/orgs/{org}/memberships/{username}"
        response = requests.put(
            url,
            json={"role": role},
            headers=headers,
            timeout=timeout,
        )
        ok = response.status_code in (200, 201, 204)
        return SyncResult(
            success=ok,
            endpoint_id=endpoint.id,
            platform=self.platform_type,
            message="org membership synced" if ok else response.text[:500],
            status_code=response.status_code,
            response_body=response.text[:2000],
        )

    def _sync_team_access(self, base_url, headers, timeout, username, extra_config, endpoint):
        org = extra_config.get("org")
        team_slug = extra_config.get("team_slug")
        if not org or not team_slug:
            return SyncResult(
                success=False,
                endpoint_id=endpoint.id,
                platform=self.platform_type,
                message="extra_config.org and team_slug required for GitHub access sync",
            )

        url = f"{base_url}/orgs/{org}/teams/{team_slug}/memberships/{username}"
        role = extra_config.get("team_role", "member")
        response = requests.put(
            url,
            json={"role": role},
            headers=headers,
            timeout=timeout,
        )
        ok = response.status_code in (200, 201, 204)
        return SyncResult(
            success=ok,
            endpoint_id=endpoint.id,
            platform=self.platform_type,
            message="team access synced" if ok else response.text[:500],
            status_code=response.status_code,
            response_body=response.text[:2000],
        )
