# Generated manually

from django.db import migrations, models
from django.utils.text import slugify


def populate_role_slugs(apps, schema_editor):
    Role = apps.get_model("userspermissionsystem", "Role")
    for role in Role.objects.all():
        if role.slug:
            continue
        base = slugify(role.name) or "role"
        slug = base
        counter = 1
        while Role.objects.filter(slug=slug).exclude(pk=role.pk).exists():
            slug = f"{base}-{counter}"
            counter += 1
        role.slug = slug
        role.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("userspermissionsystem", "0013_platform_adapters"),
    ]

    operations = [
        migrations.AddField(
            model_name="role",
            name="description",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="role",
            name="slug",
            field=models.SlugField(
                blank=True,
                help_text="Programmatic role key. Auto-filled from name when empty.",
                max_length=100,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="role",
            name="permissions",
            field=models.ManyToManyField(
                blank=True, related_name="roles", to="userspermissionsystem.appurlpermission"
            ),
        ),
        migrations.AlterModelOptions(
            name="role",
            options={"ordering": ("name",)},
        ),
        migrations.RunPython(populate_role_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="role",
            name="slug",
            field=models.SlugField(
                blank=True,
                help_text="Programmatic role key. Auto-filled from name when empty.",
                max_length=100,
                unique=True,
            ),
        ),
    ]
