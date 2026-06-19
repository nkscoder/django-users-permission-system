from django.urls import include, path

urlpatterns = [
    path("permissions/", include("userspermissionsystem.urls")),
]
