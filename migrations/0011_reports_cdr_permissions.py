from django.db import migrations


def create_reports_cdr_permissions(apps, schema_editor):
    AppModule = apps.get_model("userspermissionsystem", "AppModule")
    AppURLPermission = apps.get_model("userspermissionsystem", "AppURLPermission")

    module, _ = AppModule.objects.get_or_create(
        label="report_management_system",
        defaults={
            "name": "Report Management System",
            "is_active": True,
            "show_in_home": True,
        },
    )

    permissions = [
        ("cdr_list", "GET", "cdr/list", "CDR List"),
        ("cdr_edit_view", "GET", "edit/<int:id>/", "CDR Edit (View)"),
        ("cdr_edit", "POST", "edit/<int:id>/", "CDR Edit (Save)"),
        ("cdr_add", "POST", "add/", "CDR Add"),
    ]

    for code, method, url, name in permissions:
        AppURLPermission.objects.get_or_create(
            app=module,
            url=url,
            method=method,
            code=code,
            defaults={"name": name, "is_active": True},
        )


def remove_reports_cdr_permissions(apps, schema_editor):
    AppURLPermission = apps.get_model("userspermissionsystem", "AppURLPermission")
    AppURLPermission.objects.filter(
        code__in=["cdr_list", "cdr_edit_view", "cdr_edit", "cdr_add"],
        app__label="reports",
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("userspermissionsystem", "0010_alter_externalsyncendpoint_event_type"),
    ]

    operations = [
        migrations.RunPython(create_reports_cdr_permissions, remove_reports_cdr_permissions),
    ]
