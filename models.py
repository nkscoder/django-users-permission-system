# models.py
from django.conf import settings
from django.db import models

class AppModule(models.Model):
    label = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    icon_path = models.CharField(max_length=200, blank=True)
    icon_file = models.FileField(upload_to="module_icons/", null=True, blank=True)
    is_external = models.BooleanField(
        default=False,
        help_text="Check if this module links to an external system or API.",
    )
    base_url = models.URLField(
        blank=True,
        null=True,
        help_text="Base URL for this module's external API.",
    )

    redirect_url = models.URLField(
        blank=True, null=True,
        help_text="Final landing page after successful login (optional)."
    )
    external_api_url = models.URLField(blank=True, null=True, help_text="API endpoint for external module login (used if 'is_external' is True).")
    url_name = models.CharField(max_length=200, blank=True, help_text="Django named URL for internal navigation.")
    show_in_home = models.BooleanField(default=True,help_text="Show this module in the home page menu.")
    is_active = models.BooleanField(default=True, help_text="Is this module currently active?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
    def get_api_url(self, path: str) -> str:
        """
        Build a full API URL for this module.
        Example:
            module.get_api_url("/api/register/user/")
        """
        if not self.base_url:
            raise ValueError(f"AppModule '{self.label}' has no base_url configured")
        return self.base_url.rstrip("/") + "/" + path.lstrip("/")
    

class AppURLPermission(models.Model):
    app = models.ForeignKey(AppModule, on_delete=models.CASCADE, related_name='permissions')
    url = models.CharField(max_length=255)
    method = models.CharField(max_length=10, default='GET')
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('app', 'url', 'method', 'code')

    def __str__(self):
        return f"{self.app.label} - {self.code} ({self.method} {self.url})"

class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        help_text="Programmatic role key. Auto-filled from name when empty.",
    )
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(AppURLPermission, related_name="roles", blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify

            base = slugify(self.name) or "role"
            slug = base
            counter = 1
            while Role.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_permission_codes(self):
        return list(self.permissions.filter(is_active=True).values_list("code", flat=True))

class AppModuleAlias(models.Model):
    """Map URL prefixes to AppModule labels for generic multi-app routing."""
    module = models.ForeignKey(
        AppModule, on_delete=models.CASCADE, related_name="aliases"
    )
    alias = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "App module aliases"

    def __str__(self):
        return f"{self.alias} → {self.module.label}"


class UserAccessControl(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="url_access",
    )
    roles = models.ManyToManyField(Role, blank=True, related_name='users')
    permissions = models.ManyToManyField(AppURLPermission, blank=True, related_name='users')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user}'s Access"

    def get_all_permissions(self):
        perms = set(self.permissions.filter(is_active=True))
        for role in self.roles.filter(is_active=True):
            perms.update(role.permissions.filter(is_active=True))
        return perms

    def get_role_names(self):
        return list(self.roles.filter(is_active=True).values_list("name", flat=True))

    def get_role_slugs(self):
        return list(self.roles.filter(is_active=True).values_list("slug", flat=True))

    def has_role(self, role_name_or_slug):
        target = (role_name_or_slug or "").strip().lower()
        if not target:
            return False
        for name, slug in self.roles.filter(is_active=True).values_list("name", "slug"):
            if name.strip().lower() == target or (slug or "").strip().lower() == target:
                return True
        return False

    def has_code(self, code, app_label=None):
        from userspermissionsystem.role_permissions import user_has_permission_code

        return user_has_permission_code(self.user, code, app_label=app_label)

    def has_module_access(self, module_label):
        from userspermissionsystem.role_permissions import user_has_module_access

        return user_has_module_access(self.user, module_label)

    def get_permission_codes(self, app_label=None):
        from userspermissionsystem.role_permissions import get_user_permission_codes

        return sorted(get_user_permission_codes(self.user, app_label=app_label))

    def is_allowed(self, url, method='GET', app_label=None):
        from userspermissionsystem.url_permissions import (
            app_labels_compatible,
            extract_app_label_from_url,
            permission_path_matches,
        )

        if app_label is None:
            app_label = extract_app_label_from_url(url)

        normalized_url = url.strip('/')
        url_parts = normalized_url.split('/')
        if len(url_parts) > 1:
            normalized_url = '/'.join(url_parts[1:])
        else:
            normalized_url = url_parts[0]

        for perm in self.get_all_permissions():
            if perm.method.upper() != method.upper():
                continue

            perm_app_label = getattr(getattr(perm, "app", None), "label", None)
            if not app_labels_compatible(app_label, perm_app_label):
                continue

            perm_url = perm.url.strip('/')
            if perm_url == normalized_url:
                return True

            if permission_path_matches(perm_url, normalized_url):
                return True

        return False



class ExternalSyncEndpoint(models.Model):
    EVENT_CHOICES = [
        ("create", "User Create"),
        ("password", "Password Change"),
        ("status", "Status Change"),
        ("update", "User Update"),
        ("access", "Access/Permission Sync"),
    ]

    PLATFORM_CHOICES = [
        ("http", "Generic HTTP"),
        ("gitlab", "GitLab"),
        ("github", "GitHub"),
        ("bitbucket", "Bitbucket"),
        ("gitea", "Gitea / Forgejo"),
        ("pypi", "PyPI / Package Registry"),
        ("custom", "Custom Adapter"),
    ]

    app = models.ForeignKey(AppModule, on_delete=models.CASCADE, related_name="sync_endpoints")
    event_type = models.CharField(max_length=50, choices=EVENT_CHOICES)
    platform_type = models.CharField(
        max_length=50,
        choices=PLATFORM_CHOICES,
        default="http",
        help_text="Target platform adapter used for this sync endpoint.",
    )
    endpoint = models.CharField(
        max_length=255,
        blank=True,
        help_text="Relative API path (HTTP/PyPI) or optional override path for platform APIs.",
    )
    auth_config = models.JSONField(
        default=dict,
        blank=True,
        help_text='Auth settings, e.g. {"token": "...", "token_type": "Bearer"}',
    )
    extra_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Platform-specific options (org, group_id, workspace, scopes, etc.).",
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("app", "event_type", "platform_type")

    def __str__(self):
        return f"{self.app.label} - {self.event_type}"