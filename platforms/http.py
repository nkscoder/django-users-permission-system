import logging
from typing import Any, Dict, List, Optional

import requests

from userspermissionsystem.platforms.base import PlatformAdapter, SyncResult

logger = logging.getLogger(__name__)


class HttpAdapter(PlatformAdapter):
    """Generic HTTP POST — backward compatible with existing SPYDER-style sync."""

    platform_type = "http"

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
        timeout = int(extra_config.get("timeout", 10))
        method = (extra_config.get("method") or "POST").upper()

        try:
            url = endpoint.app.get_api_url(endpoint.endpoint)
        except Exception as exc:
            return SyncResult(
                success=False,
                endpoint_id=endpoint.id,
                platform=self.platform_type,
                message=str(exc),
                errors=[str(exc)],
            )

        body = dict(payload)
        if event_type == "access" and permissions is not None:
            body["permissions"] = [
                {
                    "code": getattr(p, "code", ""),
                    "url": getattr(p, "url", ""),
                    "method": getattr(p, "method", "GET"),
                    "app": getattr(getattr(p, "app", None), "label", ""),
                }
                for p in permissions
            ]

        headers = self._auth_headers(auth_config)
        try:
            response = requests.request(
                method,
                url,
                json=body,
                headers=headers,
                timeout=timeout,
            )
            ok = response.status_code in (200, 201, 202, 204)
            return SyncResult(
                success=ok,
                endpoint_id=endpoint.id,
                platform=self.platform_type,
                message="synced" if ok else "request failed",
                status_code=response.status_code,
                response_body=response.text[:2000],
            )
        except Exception as exc:
            logger.exception("HTTP sync failed for %s", url)
            return SyncResult(
                success=False,
                endpoint_id=endpoint.id,
                platform=self.platform_type,
                message=str(exc),
                errors=[str(exc)],
            )
