import importlib
import logging
from typing import Dict, Optional, Type

from userspermissionsystem.conf import get_permission_plugins
from userspermissionsystem.plugins.base import PermissionPlugin

logger = logging.getLogger(__name__)

_REGISTRY: Dict[str, PermissionPlugin] = {}


def register_plugin(plugin: PermissionPlugin) -> None:
    label = (plugin.label or plugin.__class__.__name__).strip().lower()
    if not label:
        raise ValueError("PermissionPlugin must define a non-empty label")
    _REGISTRY[label] = plugin


def get_plugin(label: str) -> Optional[PermissionPlugin]:
    return _REGISTRY.get((label or "").strip().lower())


def get_all_plugins() -> Dict[str, PermissionPlugin]:
    return dict(_REGISTRY)


def _load_plugin_class(dotted_path: str) -> Type[PermissionPlugin]:
    module_path, class_name = dotted_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    plugin_cls = getattr(module, class_name)
    if not issubclass(plugin_cls, PermissionPlugin):
        raise TypeError(f"{dotted_path} is not a PermissionPlugin subclass")
    return plugin_cls


def discover_plugins() -> None:
    for dotted_path in get_permission_plugins():
        try:
            plugin_cls = _load_plugin_class(dotted_path)
            register_plugin(plugin_cls())
        except Exception:
            logger.exception("Failed to load permission plugin: %s", dotted_path)
