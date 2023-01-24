from django.shortcuts import render
from django.conf import settings


def page_not_found_view(request, exception):
    base_url = settings.PRODUCTION_URL
    return render(request, "404.html", status=404, context={"base_url": base_url})


def handler500(request, *args, **argv):
    base_url = settings.PRODUCTION_URL
    return render(request, "500.html", status=500, context={"base_url": base_url})
