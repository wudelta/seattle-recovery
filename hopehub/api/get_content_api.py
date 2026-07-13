# this is a test of diff slider

from django.http import JsonResponse


PUBLIC_CONTENT_PAYLOAD = {
    "status": "success",
    "visibility": "public",
    "endpoint": "get_content",
    "app": "hopehub",
}


def get_content_endpoint(request):
    """Return the public HopeHub content endpoint payload."""
    return JsonResponse(dict(PUBLIC_CONTENT_PAYLOAD))