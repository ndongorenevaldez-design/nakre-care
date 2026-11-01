from django.urls import path
from apps.website import views

# No admin/auth/intake URLs until MFA and authorization have been implemented.
urlpatterns = [
    path("", views.home, name="home"),
    path("recrutement/", views.recruitment, name="recruitment"),
    path("robots.txt", views.robots),
    path("sitemap.xml", views.sitemap),
]
