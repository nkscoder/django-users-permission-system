import re

from userspermissionsystem.conf import get_label_groups


def _get_app_label_groups():
    return get_label_groups()


def _get_db_alias_groups():
    try:
        from userspermissionsystem.models import AppModuleAlias

        groups = {}
        for row in AppModuleAlias.objects.select_related("module").all():
            label = (row.module.label or "").strip().lower()
            alias = (row.alias or "").strip().lower()
            if not label or not alias:
                continue
            groups.setdefault(label, set()).add(label)
            groups[label].add(alias)
        return tuple(frozenset(values) for values in groups.values())
    except Exception:
        return ()


def _iter_label_groups():
    seen = set()
    for group in _get_app_label_groups():
        key = tuple(sorted(group))
        if key not in seen:
            seen.add(key)
            yield group
    for group in _get_db_alias_groups():
        key = tuple(sorted(group))
        if key not in seen:
            seen.add(key)
            yield group


def extract_app_label_from_url(url):
    parts = (url or "").strip("/").split("/")
    return parts[0] if len(parts) > 1 else None


def app_labels_compatible(request_label, perm_label):
    """True when a permission row belongs to the same app as the request path."""
    if not request_label:
        return True

    req = (request_label or "").strip().lower()
    perm = (perm_label or "").strip().lower()
    if not perm:
        return False
    if req == perm:
        return True

    for group in _iter_label_groups():
        if req in group and perm in group:
            return True

    try:
        from userspermissionsystem.plugins.registry import get_all_plugins

        for plugin in get_all_plugins().values():
            aliases = {a.strip().lower() for a in plugin.get_label_aliases()}
            if req in aliases and perm in aliases:
                return True
    except Exception:
        pass

    return False


def strip_app_prefix(url):
    normalized = (url or "").strip("/")
    parts = normalized.split("/")
    if len(parts) > 1:
        return "/".join(parts[1:])
    return normalized


def permission_path_matches(perm_url, request_url):
    """Match permission URL patterns like edit/<int:id>/ to edit/42."""
    perm_url = (perm_url or "").strip("/")
    request_url = (request_url or "").strip("/")
    if not perm_url or not request_url:
        return False
    if perm_url == request_url:
        return True

    perm_base = perm_url.split("<", 1)[0].rstrip("/")
    if perm_base and request_url.startswith(perm_base + "/"):
        tail = request_url[len(perm_base) + 1 :]
        if tail.isdigit() or not tail:
            return True

    regex_parts = []
    for segment in perm_url.split("/"):
        if segment.startswith("<") and segment.endswith(">"):
            regex_parts.append("[^/]+")
        else:
            regex_parts.append(re.escape(segment))
    pattern = "^" + "/".join(regex_parts) + "$"
    return bool(re.match(pattern, request_url))
