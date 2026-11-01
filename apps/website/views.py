from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe


@require_safe
def home(request):
    return render(request, "website/home.html")


@require_safe
def recruitment(request):
    return render(request, "website/recruitment.html")


@require_safe
def robots(request):
    return HttpResponse("User-agent: *\nDisallow: /\n", content_type="text/plain")


@require_safe
def sitemap(request):
    return render(request, "website/sitemap.xml", content_type="application/xml")
