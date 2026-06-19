from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

from .models import (
    AppModule,
    AppModuleAlias,
    AppURLPermission,
    ExternalSyncEndpoint,
    Role,
    UserAccessControl,
)


admin.site.site_header = "Users Permission System"
admin.site.index_title = "Permission Administration"


def _dashboard_link():
    try:
        url = reverse("userspermissionsystem:ai_dashboard")
        docs = reverse("userspermissionsystem:documentation")
        return format_html(
            '<a href="{}">AI Dashboard</a> · <a href="{}">Documentation</a>',
            url,
            docs,
        )
    except Exception:
        return "Mount userspermissionsystem.urls at /permissions/ to enable dashboard."


@admin.register(AppModule)
class AppModuleAdmin(ImportExportModelAdmin):
    list_display = ("label", "name", "is_active", "is_external")
    search_fields = ("label", "name")

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["dashboard_links"] = _dashboard_link()
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(AppURLPermission)
class AppURLPermissionAdmin(ImportExportModelAdmin):
    list_display = ('app', 'code', 'name', 'url', 'method', 'is_active')
    list_filter = ('app', 'method', 'is_active')
    search_fields = ('code', 'url', 'name')


@admin.register(Role)
class RoleAdmin(ImportExportModelAdmin):
    list_display = ("name", "slug", "is_active", "permission_count")
    filter_horizontal = ("permissions",)
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}

    def permission_count(self, obj):
        return obj.permissions.filter(is_active=True).count()

    permission_count.short_description = "Permissions"


@admin.register(UserAccessControl)
class UserAccessControlAdmin(ImportExportModelAdmin):
    list_display = ('user', 'get_roles', 'get_permissions')
    filter_horizontal = ('roles', 'permissions')
    search_fields = ('user__username', 'user__email')

    def get_roles(self, obj):
        return ", ".join([role.name for role in obj.roles.all()])
    get_roles.short_description = 'Roles'

    def get_permissions(self, obj):
        return ", ".join([perm.code for perm in obj.permissions.all()])
    get_permissions.short_description = 'Direct Permissions'



@admin.register(AppModuleAlias)
class AppModuleAliasAdmin(ImportExportModelAdmin):
    list_display = ("alias", "module", "created_at")
    search_fields = ("alias", "module__label", "module__name")
    list_filter = ("module",)


@admin.register(ExternalSyncEndpoint)
class ExternalSyncEndpointAdmin(ImportExportModelAdmin):
    list_display = (
        "id",
        "app",
        "event_type",
        "platform_type",
        "endpoint",
        "is_active",
        "created_at",
    )
    list_filter = ("event_type", "platform_type", "is_active", "app")
    search_fields = ("event_type", "endpoint", "app__label")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("app", "event_type")

