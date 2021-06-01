from django.urls import path
from . import views

app_name = "snapms"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("submit", views.handle_snapms, name="handle_snapms"),
    path("output/<uuid:job_id>", views.job_output, name="job_output"),
    path("docs", views.docs, name="docs"),
]
