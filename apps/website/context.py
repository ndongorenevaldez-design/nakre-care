from django.conf import settings


def brand(request):
    return {
        "public_origin": settings.PUBLIC_ORIGIN,
        "whatsapp_url": f"https://wa.me/{settings.WHATSAPP_NUMBER}",
    }
