"""Generic role and permission helpers for any Django project."""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional, Set, Union

from userspermissionsystem.conf import get_admin_role_names, get_permission_code_groups
from userspermissionsystem.models import AppModule, UserAccessControl
from userspermissionsystem.url_permissions import app_labels_compatible


def normalize_permission_key(code="", name="", url="") -> str:
    for raw in (code, name, url):
        if not raw:
            continue
        key = re.sub(r"[^a-z0-9]+", "_", str(raw).strip().lower()).strip("_")
        if key:
            return key
    return ""


def get_user_access(user) -> Optional[UserAccessControl]:
    if not user or not getattr(user, "is_authenticated", False):
        return None
    if getattr(user, "is_superuser", False):
        return getattr(user, "url_access", None)
    return getattr(user, "url_access", None)


def user_is_privileged(user) -> bool:
    if not user or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False):
        return True
    admin_names = {name.strip().lower() for name in get_admin_role_names()}
    user_roles = {role.strip().lower() for role in get_user_roles(user)}
    return bool(admin_names & user_roles)


def get_user_roles(user) -> List[str]:
    access = get_user_access(user)
    if not access:
        return []
    return list(access.roles.filter(is_active=True).values_list("name", flat=True))


def user_has_role(user, role_name: str) -> bool:
    if not role_name:
        return False
    target = role_name.strip().lower()
    return any(role.strip().lower() == target for role in get_user_roles(user))


def user_has_any_role(user, role_names: Iterable[str]) -> bool:
    targets = {name.strip().lower() for name in role_names if name}
    if not targets:
        return False
    user_roles = {role.strip().lower() for role in get_user_roles(user)}
    return bool(targets & user_roles)


def get_user_permission_codes(user, app_label: Optional[str] = None) -> Set[str]:
    access = get_user_access(user)
    if not access:
        return set()

    codes: Set[str] = set()
    for perm in access.get_all_permissions():
        perm_app = getattr(getattr(perm, "app", None), "label", None)
        if app_label and not app_labels_compatible(app_label, perm_app):
            continue
        code = (getattr(perm, "code", "") or "").strip()
        if code:
            codes.add(code)
    return codes


def user_has_permission_code(user, code: str, app_label: Optional[str] = None) -> bool:
    if not code:
        return False
    if getattr(user, "is_superuser", False):
        return True
    target = code.strip().lower()
    access = get_user_access(user)
    if not access:
        return False

    for perm in access.get_all_permissions():
        perm_app = getattr(getattr(perm, "app", None), "label", None)
        if app_label and not app_labels_compatible(app_label, perm_app):
            continue
        if (getattr(perm, "code", "") or "").strip().lower() == target:
            return True
    return False


def user_has_url_permission(
    user,
    url: str,
    method: str = "GET",
    app_label: Optional[str] = None,
) -> bool:
    if getattr(user, "is_superuser", False):
        return True
    access = get_user_access(user)
    if not access:
        return False
    return access.is_allowed(url, method, app_label=app_label)


def get_module_labels(module_label: str) -> Set[str]:
    labels = {(module_label or "").strip().lower()}
    try:
        module = AppModule.objects.filter(label__iexact=module_label, is_active=True).first()
        if module:
            labels.add(module.label.strip().lower())
            for alias in module.aliases.all():
                labels.add(alias.alias.strip().lower())
    except Exception:
        pass
    return {label for label in labels if label}


def get_module_ids(module_label: str) -> Set[int]:
    from django.db.models import Q

    labels = get_module_labels(module_label)
    if not labels:
        return set()

    query = Q()
    for label in labels:
        query |= Q(label__iexact=label) | Q(aliases__alias__iexact=label)
    return set(AppModule.objects.filter(is_active=True).filter(query).values_list("id", flat=True))


def user_has_module_access(user, module_label: str) -> bool:
    if not user or not getattr(user, "is_active", True):
        return False
    if getattr(user, "is_superuser", False):
        return True

    access = get_user_access(user)
    if not access:
        return False

    module_ids = get_module_ids(module_label)
    if module_ids:
        for perm in access.get_all_permissions():
            if getattr(perm, "app_id", None) in module_ids:
                return True

    labels = get_module_labels(module_label)
    for perm in access.get_all_permissions():
        perm_label = (getattr(getattr(perm, "app", None), "label", "") or "").strip().lower()
        if perm_label in labels:
            return True
        for label in labels:
            if app_labels_compatible(label, perm_label):
                return True

    for role in access.roles.filter(is_active=True):
        role_name = (role.name or "").strip().lower()
        if any(label in role_name for label in labels):
            return True

    return False


def get_grouped_permissions(
    user,
    code_map: Optional[Dict[str, tuple]] = None,
) -> Dict[str, Dict[str, bool]]:
    """
    Build nested permission flags from assigned codes.

    code_map example:
        {"orders_create": ("orders", "create"), "orders_view": ("orders", "view")}
    """
    code_map = code_map or get_permission_code_groups()
    result: Dict[str, Dict[str, bool]] = {}

    for raw_key, mapping in code_map.items():
        if not mapping or len(mapping) != 2:
            continue
        module_key, action_key = mapping
        result.setdefault(module_key, {})
        result[module_key][action_key] = False

    if not user or not getattr(user, "is_authenticated", False):
        return result

    access = get_user_access(user)
    if not access:
        return result

    for perm in access.get_all_permissions():
        key = normalize_permission_key(
            getattr(perm, "code", ""),
            getattr(perm, "name", ""),
            getattr(perm, "url", ""),
        )
        mapping = code_map.get(key)
        if not mapping:
            continue
        module_key, action_key = mapping
        result.setdefault(module_key, {})
        result[module_key][action_key] = True

    return result


def user_has_grouped_action(user, module_key: str, action_key: str) -> bool:
    groups = get_grouped_permissions(user)
    return bool(groups.get(module_key, {}).get(action_key))


def get_allowed_modules_for_user(user):
    if not user or not getattr(user, "is_authenticated", False):
        return AppModule.objects.none()

    access = get_user_access(user)
    if not access:
        return AppModule.objects.none()

    allowed_labels: Set[str] = set()
    for perm in access.get_all_permissions():
        label = getattr(getattr(perm, "app", None), "label", None)
        if label:
            allowed_labels.add(label)

    if not allowed_labels:
        return AppModule.objects.none()

    return AppModule.objects.filter(
        label__in=allowed_labels,
        show_in_home=True,
        is_active=True,
    ).order_by("name")
