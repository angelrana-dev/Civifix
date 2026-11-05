from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("report/", views.report, name="report"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("issue/<int:pk>/", views.detail, name="detail"),
    path("api/issues/", views.api_issues, name="api_issues"),
    path("api/issue/<int:pk>/", views.api_issue, name="api_issue"),
]