from userspermissionsystem.platforms.base import PlatformAdapter, SyncResult
from userspermissionsystem.platforms.registry import (
    get_platform_adapter,
    register_platform_adapter,
)

__all__ = [
    "PlatformAdapter",
    "SyncResult",
    "get_platform_adapter",
    "register_platform_adapter",
]
