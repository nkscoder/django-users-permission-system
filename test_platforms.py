from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, override_settings

from userspermissionsystem.platforms.http import HttpAdapter
from userspermissionsystem.platforms.registry import get_platform_adapter, register_builtin_adapters
from userspermissionsystem.url_permissions import app_labels_compatible


class PlatformRegistryTests(SimpleTestCase):
    def test_builtin_adapters_are_registered(self):
        register_builtin_adapters()
        self.assertEqual(get_platform_adapter("gitlab").platform_type, "gitlab")
        self.assertEqual(get_platform_adapter("github").platform_type, "github")
        self.assertEqual(get_platform_adapter("pypi").platform_type, "pypi")
        self.assertEqual(get_platform_adapter("gitea").platform_type, "gitea")
        self.assertEqual(get_platform_adapter("bitbucket").platform_type, "bitbucket")

    def test_unknown_platform_falls_back_to_http(self):
        register_builtin_adapters()
        self.assertEqual(get_platform_adapter("unknown").platform_type, "http")


class HttpAdapterTests(SimpleTestCase):
    @patch("userspermissionsystem.platforms.http.requests.request")
    def test_http_adapter_posts_payload(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.text = "ok"
        mock_request.return_value = mock_response

        endpoint = SimpleNamespace(
            id=1,
            endpoint="/api/register/user/",
            auth_config={"token": "secret"},
            extra_config={},
            app=SimpleNamespace(
                base_url="https://example.com",
                get_api_url=lambda path: f"https://example.com{path}",
            ),
        )
        user = SimpleNamespace(username="alice", email="alice@example.com")
        result = HttpAdapter().sync(endpoint, "create", user, {"username": "alice"})

        self.assertTrue(result.success)
        mock_request.assert_called_once()
        self.assertEqual(
            mock_request.call_args.kwargs["json"]["username"],
            "alice",
        )


@override_settings(
    USER_PERMISSION_SYSTEM={
        "LABEL_GROUPS": [
            ["alpha", "beta"],
        ]
    }
)
class ConfigurableLabelGroupTests(SimpleTestCase):
    def test_settings_label_groups_are_used(self):
        self.assertTrue(app_labels_compatible("alpha", "beta"))
        self.assertFalse(app_labels_compatible("alpha", "gamma"))
