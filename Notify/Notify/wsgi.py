import os
from django.core.wsgi import get_wsgi_application

#estamos 99% seguros q esto no se usa, pero lo dejamos para no tocar el settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Notify.settings')
application = get_wsgi_application()
