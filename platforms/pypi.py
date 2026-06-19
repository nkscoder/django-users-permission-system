import logging
from typing import Any, Dict, List, Optional

import requests

from userspermissionsystem.platforms.base import PlatformAdapter, SyncResult

logger = logging.getLogger(__name__)


class PyPIAdapter(PlatformAdapter):
    """
    PyPI / package registry integration.

    Public PyPI has no user-provisioning API. This adapter supports:
    - Self-hosted Warehouse instances with a custom token endpoint
    - Webhook-style notification of permission changes for external automation
    - Token metadata sync via configurable endpoint paths
    """

    platform_type = "pypi"

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
        base_url = (endpoint.app.base_url or "").rstrip("/")
        headers = self._auth_headers(auth_config)
        timeout = int(extra_config.get("timeout", 10))
        username = self._username(user, payload)

        body = {
            "event_type": event_type,
            "username": username,
            "email": payload.get("email") or getattr(user, "email", ""),
            "pypi_username": extra_config.get("pypi_username") or username,
            "scopes": extra_config.get("scopes", ["upload"]),
        }
        if event_type == "access" and permissions is not None:
            body["permissions"] = [
                getattr(p, "code", str(p)) for p in permissions
            ]
        if event_type == "password":
            body["action"] = "rotate_token"
        elif event_type == "create":
            body["action"] = "provision_token"
        elif event_type == "status":
            body["action"] = "revoke" if not payload.get("is_approved", True) else "activate"
        else:
            body["action"] = "sync"

        path = endpoint.endpoint or extra_config.get(
            "token_endpoint", "/api/v1/tokens/sync/"
        )
        url = f"{base_url}/{path.lstrip('/')}"

        try:
            response = requests.post(url, json=body, headers=headers, timeout=timeout)
            ok = response.status_code in (200, 201, 202, 204)
            return SyncResult(
                success=ok,
                endpoint_id=endpoint.id,
                platform=self.platform_type,
                message="pypi sync completed" if ok else response.text[:500],
                status_code=response.status_code,
                response_body=response.text[:2000],
            )
        except Exception as exc:
            logger.exception("PyPI sync failed for %s", url)
            return SyncResult(
                success=False,
                endpoint_id=endpoint.id,
                platform=self.platform_type,
                message=str(exc),
                errors=[str(exc)],
            )
