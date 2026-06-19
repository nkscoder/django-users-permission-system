from django.apps import AppConfig


class UserspermissionsystemConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "userspermissionsystem"

    def ready(self):
        from userspermissionsystem.plugins.registry import discover_plugins
        from userspermissionsystem.platforms.registry import register_builtin_adapters

        register_builtin_adapters()
        discover_plugins()
