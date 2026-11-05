from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", auth.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth.LogoutView.as_view(), name="logout"),
    path("", include("issues.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
