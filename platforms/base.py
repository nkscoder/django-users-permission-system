from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SyncResult:
    success: bool
    endpoint_id: Optional[int] = None
    platform: str = ""
    message: str = ""
    status_code: Optional[int] = None
    response_body: str = ""
    errors: List[str] = field(default_factory=list)


class PlatformAdapter(ABC):
    """Sync user lifecycle events to an external platform."""

    platform_type: str = ""

    @abstractmethod
    def sync(
        self,
        endpoint,
        event_type: str,
        user,
        payload: Dict[str, Any],
        permissions: Optional[List[Any]] = None,
    ) -> SyncResult:
        pass

    def _auth_headers(self, auth_config: Dict[str, Any]) -> Dict[str, str]:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        token = auth_config.get("token") or auth_config.get("api_token")
        token_type = (auth_config.get("token_type") or "Bearer").strip()
        if token:
            if token_type.lower() == "private-token":
                headers["PRIVATE-TOKEN"] = token
            elif token_type.lower() == "basic":
                import base64

                user = auth_config.get("username", "")
                password = auth_config.get("password", token)
                encoded = base64.b64encode(f"{user}:{password}".encode()).decode()
                headers["Authorization"] = f"Basic {encoded}"
            else:
                headers["Authorization"] = f"{token_type} {token}"
        for key, value in (auth_config.get("headers") or {}).items():
            headers[str(key)] = str(value)
        return headers

    def _username(self, user, payload: Dict[str, Any]) -> str:
        return (
            payload.get("username")
            or getattr(user, "username", None)
            or getattr(user, "email", None)
            or getattr(user, "phone_no", None)
            or ""
        )
