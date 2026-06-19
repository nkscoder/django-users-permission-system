import importlib
import logging
from typing import Dict, Optional, Type

from userspermissionsystem.conf import get_platform_adapters
from userspermissionsystem.platforms.base import PlatformAdapter

logger = logging.getLogger(__name__)

_REGISTRY: Dict[str, PlatformAdapter] = {}


def register_platform_adapter(adapter: PlatformAdapter) -> None:
    platform = (adapter.platform_type or adapter.__class__.__name__).strip().lower()
    if not platform:
        raise ValueError("PlatformAdapter must define platform_type")
    _REGISTRY[platform] = adapter


def get_platform_adapter(platform_type: str) -> PlatformAdapter:
    key = (platform_type or "http").strip().lower()
    adapter = _REGISTRY.get(key)
    if adapter is None:
        from userspermissionsystem.platforms.http import HttpAdapter

        return HttpAdapter()
    return adapter


def _load_adapter_class(dotted_path: str) -> Type[PlatformAdapter]:
    module_path, class_name = dotted_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    adapter_cls = getattr(module, class_name)
    if not issubclass(adapter_cls, PlatformAdapter):
        raise TypeError(f"{dotted_path} is not a PlatformAdapter subclass")
    return adapter_cls


def discover_platform_adapters() -> None:
    for platform_type, dotted_path in get_platform_adapters().items():
        try:
            adapter_cls = _load_adapter_class(dotted_path)
            adapter = adapter_cls()
            register_platform_adapter(adapter)
        except Exception:
            logger.exception(
                "Failed to load platform adapter %s=%s", platform_type, dotted_path
            )


def get_registered_platforms():
    return sorted(_REGISTRY.keys())


def register_builtin_adapters() -> None:
    from userspermissionsystem.platforms.bitbucket import BitbucketAdapter
    from userspermissionsystem.platforms.gitea import GiteaAdapter
    from userspermissionsystem.platforms.github import GitHubAdapter
    from userspermissionsystem.platforms.gitlab import GitLabAdapter
    from userspermissionsystem.platforms.http import HttpAdapter
    from userspermissionsystem.platforms.pypi import PyPIAdapter

    for adapter in (
        HttpAdapter(),
        GitLabAdapter(),
        GitHubAdapter(),
        BitbucketAdapter(),
        GiteaAdapter(),
        PyPIAdapter(),
    ):
        register_platform_adapter(adapter)

    discover_platform_adapters()
