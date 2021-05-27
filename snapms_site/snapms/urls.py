from django.urls import path
from . import views

app_name = "snapms"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("docs", views.docs, name="docs"),
]
