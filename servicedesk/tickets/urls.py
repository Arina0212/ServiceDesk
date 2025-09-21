from django.urls import path
from . import views

urlpatterns = [
    # Другие URL...
    path('api/inbound-email/', views.inbound_email_webhook, name='inbound_email'),
]
