from django.urls import path
from . import views

app_name = "snapms"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("submit", views.handle_snapms, name="handle_snapms"),
    path("docs", views.docs, name="docs"),
]
