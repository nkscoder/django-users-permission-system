from django.test import SimpleTestCase, override_settings

from userspermissionsystem.role_permissions import (
    get_grouped_permissions,
    normalize_permission_key,
    user_has_any_role,
)
from userspermissionsystem.url_permissions import (
    app_labels_compatible,
    permission_path_matches,
)


@override_settings(
    USER_PERMISSION_SYSTEM={
        "LABEL_GROUPS": [
            ["billing", "invoices"],
            ["orders", "order"],
        ],
        "ADMIN_ROLE_NAMES": ["admin", "supervisor"],
        "PERMISSION_CODE_GROUPS": {
            "orders_create": ("orders", "create"),
            "orders_view": ("orders", "view"),
        },
    }
)
class GenericRolePermissionTests(SimpleTestCase):
    def test_configurable_label_groups(self):
        self.assertTrue(app_labels_compatible("billing", "invoices"))
        self.assertFalse(app_labels_compatible("billing", "orders"))

    def test_normalize_permission_key(self):
        self.assertEqual(normalize_permission_key("Order-Create", "", ""), "order_create")

    def test_grouped_permissions_from_settings(self):
        result = get_grouped_permissions(None)
        self.assertEqual(result["orders"]["create"], False)
        self.assertEqual(result["orders"]["view"], False)

    def test_user_has_any_role_helper(self):
        class User:
            is_authenticated = True
            is_superuser = False
            url_access = None

        self.assertFalse(user_has_any_role(User(), ["admin"]))


class PermissionPathMatchTests(SimpleTestCase):
    def test_edit_pattern_matches_numeric_id(self):
        self.assertTrue(permission_path_matches("edit/<int:id>/", "edit/42"))

    def test_exact_path_match(self):
        self.assertTrue(permission_path_matches("list", "list"))

    def test_unrelated_path_no_match(self):
        self.assertFalse(permission_path_matches("edit/<int:id>/", "list/items"))
