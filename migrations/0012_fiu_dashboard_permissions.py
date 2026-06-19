from django.db import migrations
from django.db.models import Q


FIU_MODULE_LABELS = ("fiu", "FIU", "str", "STR")
SEARCH_FIU_URL = "search_fiu/"
DASHBOARD_PERMISSIONS = (
    ("fiu_dashboard_str", "GET", "dashboard/str", "FIU Dashboard - STR Count"),
    ("fiu_dashboard_priority", "GET", "dashboard/priority", "FIU Dashboard - Case Priority"),
    ("fiu_dashboard_entities", "GET", "dashboard/entities", "FIU Dashboard - Entity Data"),
    ("fiu_dashboard_state", "GET", "dashboard/state", "FIU Dashboard - State Wise Count"),
)


def _search_fiu_permission_q():
    return (
        Q(url__iexact=SEARCH_FIU_URL)
        | Q(url__iendswith="/search_fiu/")
        | Q(code__iexact="search_fiu")
    )


def _get_fiu_module(AppModule):
    for label in FIU_MODULE_LABELS:
        module = AppModule.objects.filter(label=label).first()
        if module:
            return module
    return AppModule.objects.create(
        label="str",
        name="FIU",
        is_active=True,
        show_in_home=True,
        url_name="fiu:search_fiu",
    )


def create_fiu_dashboard_permissions(apps, schema_editor):
    AppModule = apps.get_model("userspermissionsystem", "AppModule")
    AppURLPermission = apps.get_model("userspermissionsystem", "AppURLPermission")
    Role = apps.get_model("userspermissionsystem", "Role")
    UserAccessControl = apps.get_model("userspermissionsystem", "UserAccessControl")

    module = _get_fiu_module(AppModule)
    created_perms = []

    for code, method, url, name in DASHBOARD_PERMISSIONS:
        perm, _ = AppURLPermission.objects.get_or_create(
            app=module,
            url=url,
            method=method,
            code=code,
            defaults={"name": name, "is_active": True},
        )
        created_perms.append(perm)

    search_fiu_perms = AppURLPermission.objects.filter(
        app=module,
        is_active=True,
    ).filter(_search_fiu_permission_q())

    perm_ids = list(search_fiu_perms.values_list("id", flat=True))
    if not perm_ids:
        return

    for role in Role.objects.filter(permissions__id__in=perm_ids).distinct():
        role.permissions.add(*created_perms)

    for access in UserAccessControl.objects.filter(permissions__id__in=perm_ids).distinct():
        access.permissions.add(*created_perms)


def remove_fiu_dashboard_permissions(apps, schema_editor):
    AppURLPermission = apps.get_model("userspermissionsystem", "AppURLPermission")
    codes = [row[0] for row in DASHBOARD_PERMISSIONS]
    AppURLPermission.objects.filter(code__in=codes).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("userspermissionsystem", "0011_reports_cdr_permissions"),
    ]

    operations = [
        migrations.RunPython(create_fiu_dashboard_permissions, remove_fiu_dashboard_permissions),
    ]
