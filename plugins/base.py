from abc import ABC, abstractmethod
from typing import Any


class PermissionPlugin(ABC):
    """
    Optional extension point for host apps that want to register
    module-specific permission helpers without modifying core code.
    """

    label: str = ""

    @abstractmethod
    def get_label_aliases(self) -> set[str]:
        """URL prefixes / AppModule labels treated as the same module."""

    def get_permission_codes(self) -> dict[str, Any]:
        """Optional mapping of permission codes to domain actions."""
        return {}

    def check_permission(self, user, code: str, **context) -> bool:
        """Optional custom permission check beyond URL matching."""
        return False
