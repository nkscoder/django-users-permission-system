import logging
from typing import Any, Dict, List, Optional

import requests

from userspermissionsystem.platforms.base import PlatformAdapter, SyncResult
from userspermissionsystem.platforms.gitlab import GitLabAdapter

logger = logging.getLogger(__name__)


class GiteaAdapter(GitLabAdapter):
    """
    Gitea / Forgejo / self-hosted Git — API is GitLab-compatible enough
    to reuse GitLab adapter with /api/v1 paths.
    """

    platform_type = "gitea"

    def _api(self, base_url: str, path: str) -> str:
        return f"{base_url}/api/v1{path}"

    def sync(
        self,
        endpoint,
        event_type: str,
        user,
        payload: Dict[str, Any],
        permissions: Optional[List[Any]] = None,
    ) -> SyncResult:
        try:
            return super().sync(endpoint, event_type, user, payload, permissions)
        except requests.RequestException as exc:
            logger.exception("Gitea sync failed")
            return SyncResult(
                success=False,
                endpoint_id=endpoint.id,
                platform=self.platform_type,
                message=str(exc),
                errors=[str(exc)],
            )
