# Generated manually for platform adapter support

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("userspermissionsystem", "0012_fiu_dashboard_permissions"),
    ]

    operations = [
        migrations.CreateModel(
            name="AppModuleAlias",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("alias", models.CharField(max_length=100, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "module",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aliases",
                        to="userspermissionsystem.appmodule",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "App module aliases",
            },
        ),
        migrations.AddField(
            model_name="externalsyncendpoint",
            name="auth_config",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='Auth settings, e.g. {"token": "...", "token_type": "Bearer"}',
            ),
        ),
        migrations.AddField(
            model_name="externalsyncendpoint",
            name="extra_config",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="Platform-specific options (org, group_id, workspace, scopes, etc.).",
            ),
        ),
        migrations.AddField(
            model_name="externalsyncendpoint",
            name="platform_type",
            field=models.CharField(
                choices=[
                    ("http", "Generic HTTP"),
                    ("gitlab", "GitLab"),
                    ("github", "GitHub"),
                    ("bitbucket", "Bitbucket"),
                    ("gitea", "Gitea / Forgejo"),
                    ("pypi", "PyPI / Package Registry"),
                    ("custom", "Custom Adapter"),
                ],
                default="http",
                help_text="Target platform adapter used for this sync endpoint.",
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="externalsyncendpoint",
            name="endpoint",
            field=models.CharField(
                blank=True,
                help_text="Relative API path (HTTP/PyPI) or optional override path for platform APIs.",
                max_length=255,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="externalsyncendpoint",
            unique_together={("app", "event_type", "platform_type")},
        ),
    ]
