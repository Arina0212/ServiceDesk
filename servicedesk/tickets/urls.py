from django.urls import path
from . import views

urlpatterns = [
    path('api/inbound-email/', views.inbound_email_webhook, name='inbound_email'),
    path('', views.ticket_list, name='ticket_list'),  # Главная страница
    path('ticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('ticket/<int:ticket_id>/take/', views.take_ticket, name='take_ticket'),
    path('ticket/<int:ticket_id>/close/',
         views.close_ticket, name='close_ticket'),
]
