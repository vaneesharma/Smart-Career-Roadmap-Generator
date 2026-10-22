"""
ASGI config for career_roadmap project. Used for async servers.
We don't need this actively for our project but Django expects it to exist.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'career_roadmap.settings')

application = get_asgi_application()
