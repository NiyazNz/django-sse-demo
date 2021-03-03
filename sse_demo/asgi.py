"""
ASGI config for sse project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sse_demo.settings')


# def get_asgi_application1():
#     """
#     The public interface to Django's ASGI support. Return an ASGI 3 callable.
#
#     Avoids making django.core.handlers.ASGIHandler a public API, in case the
#     internal implementation changes or moves in the future.
#     """
#     django.setup(set_prefix=False)
#     return ASGIHandler()


application = get_asgi_application()
