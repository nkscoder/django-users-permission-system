import logging
from typing import Any, Dict, List, Optional

import requests

from userspermissionsystem.platforms.base import PlatformAdapter, SyncResult

logger = logging.getLogger(__name__)


class GitLabAdapter(PlatformAdapter):
    """
    GitLab user and access sync via REST API v4.
    Docs: https://docs.gitlab.com/ee/api/users.html
    """

    platform_type = "gitlab"

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
        timeout = int(extra_config.get("timeout", 15))
        username = self._username(user, payload)
        email = payload.get("email") or getattr(user, "email", "")

        try:
            if event_type == "create":
                return self._create_user(
                    base_url, headers, timeout, username, email, payload, endpoint
                )
            if event_type == "update":
                return self._update_user(
                    base_url, headers, timeout, username, email, payload, endpoint
                )
            if event_type == "password":
                return self._change_password(
                    base_url, headers, timeout, username, payload, endpoint
                )
            if event_type == "status":
                return self._change_status(
                    base_url, headers, timeout, username, payload, endpoint
                )
            if event_type == "access":
                return self._sync_access(
                    base_url,
                    headers,
                    timeout,
                    username,
                    permissions or [],
                    extra_config,
                    endpoint,
                )
            return SyncResult(
                success=False,
                endpoint_id=endpoint.id,
                platform=self.platform_type,
                message=f"Unsupported event type: {event_type}",
            )
        except Exception as exc:
            logger.exception("GitLab sync failed")
            return SyncResult(
                success=False,
                endpoint_id=endpoint.id,
                platform=self.platform_type,
                message=str(exc),
                errors=[str(exc)],
            )

    def _api(self, base_url: str, path: str) -> str:
        return f"{base_url}/api/v4{path}"

    def _find_user_id(self, base_url, headers, timeout, username, email):
        for search in filter(None, [username, email]):
            response = requests.get(
                self._api(base_url, "/users"),
                params={"username": search},
                headers=headers,
                timeout=timeout,
            )
            if response.status_code == 200 and response.json():
                return response.json()[0]["id"]
        if email:
            response = requests.get(
                self._api(base_url, "/users"),
                params={"search": email},
                headers=headers,
                timeout=timeout,
            )
            if response.status_code == 200 and response.json():
                return response.json()[0]["id"]
        return None

    def _create_user(self, base_url, headers, timeout, username, email, payload, endpoint):
        body = {
            "username": username,
            "email": email,
            "name": f"{payload.get('first_name', '')} {payload.get('last_name', '')}".strip()
            or username,
            "skip_confirmation": True,
            "reset_password": False,
        }
        if payload.get("password"):
            body["password"] = payload["password"]
        if "is_approved" in payload:
            body["external"] = not payload["is_approved"]

        response = requests.post(
            self._api(base_url, "/users"),
            json=body,
            headers=headers,
            timeout=timeout,
        )
        ok = response.status_code in (200, 201)
        return SyncResult(
            success=ok,
            endpoint_id=endpoint.id,
            platform=self.platform_type,
            message="user created" if ok else response.text[:500],
            status_code=response.status_code,
            response_body=response.text[:2000],
        )

    def _update_user(self, base_url, headers, timeout, username, email, payload, endpoint):
        user_id = self._find_user_id(base_url, headers, timeout, username, email)
        if not user_id:
            return SyncResult(
                success=False,
                endpoint_id=endpoint.id,
                platform=self.platform_type,
                message=f"GitLab user not found: {username}",
            )
        body = {}
        if email:
            body["email"] = email
        name = f"{payload.get('first_name', '')} {payload.get('last_name', '')}".strip()
        if name:
            body["name"] = name
        response = requests.put(
            self._api(base_url, f"/users/{user_id}"),
            json=body,
            headers=headers,
            timeout=timeout,
        )
        ok = response.status_code in (200, 201)
        return SyncResult(
            success=ok,
            endpoint_id=endpoint.id,
            platform=self.platform_type,
            message="user updated" if ok else response.text[:500],
            status_code=response.status_code,
            response_body=response.text[:2000],
        )

    def _change_password(self, base_url, headers, timeout, username, payload, endpoint):
        user_id = self._find_user_id(
            base_url,
            headers,
            timeout,
            username,
            payload.get("email"),
        )
        if not user_id:
            return SyncResult(
                success=False,
                endpoint_id=endpoint.id,
                platform=self.platform_type,
                message=f"GitLab user not found: {username}",
            )
        new_password = payload.get("new_password") or payload.get("password")
        if not new_password:
            return SyncResult(
                success=False,
                endpoint_id=endpoint.id,
                platform=self.platform_type,
                message="No password provided",
            )
        response = requests.put(
            self._api(base_url, f"/users/{user_id}"),
            json={"password": new_password},
            headers=headers,
            timeout=timeout,
        )
        ok = response.status_code in (200, 201)
        return SyncResult(
            success=ok,
            endpoint_id=endpoint.id,
            platform=self.platform_type,
            message="password updated" if ok else response.text[:500],
            status_code=response.status_code,
            response_body=response.text[:2000],
        )

    def _change_status(self, base_url, headers, timeout, username, payload, endpoint):
        user_id = self._find_user_id(
            base_url,
            headers,
            timeout,
            username,
            payload.get("email"),
        )
        if not user_id:
            return SyncResult(
                success=False,
                endpoint_id=endpoint.id,
                platform=self.platform_type,
                message=f"GitLab user not found: {username}",
            )
        blocked = not payload.get("is_approved", True)
        response = requests.put(
            self._api(base_url, f"/users/{user_id}"),
            json={"blocked": blocked},
            headers=headers,
            timeout=timeout,
        )
        ok = response.status_code in (200, 201)
        return SyncResult(
            success=ok,
            endpoint_id=endpoint.id,
            platform=self.platform_type,
            message="status updated" if ok else response.text[:500],
            status_code=response.status_code,
            response_body=response.text[:2000],
        )

    def _sync_access(
        self,
        base_url,
        headers,
        timeout,
        username,
        permissions,
        extra_config,
        endpoint,
    ):
        group_id = extra_config.get("group_id")
        project_id = extra_config.get("project_id")
        access_level = int(extra_config.get("access_level", 30))
        if not group_id and not project_id:
            return SyncResult(
                success=False,
                endpoint_id=endpoint.id,
                platform=self.platform_type,
                message="extra_config.group_id or project_id required for GitLab access sync",
            )

        user_id = self._find_user_id(base_url, headers, timeout, username, None)
        if not user_id:
            return SyncResult(
                success=False,
                endpoint_id=endpoint.id,
                platform=self.platform_type,
                message=f"GitLab user not found: {username}",
            )

        if group_id:
            url = self._api(base_url, f"/groups/{group_id}/members")
        else:
            url = self._api(base_url, f"/projects/{project_id}/members")

        response = requests.post(
            url,
            json={"user_id": user_id, "access_level": access_level},
            headers=headers,
            timeout=timeout,
        )
        ok = response.status_code in (200, 201)
        return SyncResult(
            success=ok,
            endpoint_id=endpoint.id,
            platform=self.platform_type,
            message="access synced" if ok else response.text[:500],
            status_code=response.status_code,
            response_body=response.text[:2000],
        )
