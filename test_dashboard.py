from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from userspermissionsystem.dashboard import ai_assistant_reply


class AiAssistantTests(TestCase):
    def test_gitlab_question_returns_guidance(self):
        answer = ai_assistant_reply("How do I configure GitLab sync?")
        self.assertIn("gitlab", answer.lower())

    def test_unknown_question_returns_fallback(self):
        answer = ai_assistant_reply("xyzzy")
        self.assertIn("GitLab", answer)


class DashboardViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.staff = User.objects.create_user(
            username="admin",
            password="pass",
            is_staff=True,
        )
        self.client = Client()

    def test_dashboard_requires_staff(self):
        response = self.client.get(reverse("userspermissionsystem:ai_dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_renders_for_staff(self):
        self.client.login(username="admin", password="pass")
        response = self.client.get(reverse("userspermissionsystem:ai_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AI Permission Dashboard")

    def test_docs_page_renders(self):
        self.client.login(username="admin", password="pass")
        response = self.client.get(reverse("userspermissionsystem:documentation"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Documentation")
