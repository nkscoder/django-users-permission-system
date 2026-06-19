from django.urls import path

from userspermissionsystem import dashboard_views

app_name = "userspermissionsystem"

urlpatterns = [
    path("dashboard/", dashboard_views.ai_dashboard, name="ai_dashboard"),
    path("docs/", dashboard_views.documentation, name="documentation"),
    path("api/ai-assistant/", dashboard_views.ai_assistant_api, name="ai_assistant_api"),
]
