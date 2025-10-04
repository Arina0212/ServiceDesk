# Этот файл отвечает за обработку входящих писем от пользователей

from django.core.mail import send_mail
from django.conf import settings
from .models import Ticket, Message
from .email_service import send_autoreply

def process_incoming_email(from_email, subject, body):
    """
    Обрабатывает входящее письмо от пользователя.
    Ищет открытое обращение от этого email или создает новое.
    """
    try:
        # Ищем последнее НЕзакрытое обращение от этого пользователя
        # filter - это как WHERE в SQL, ищем по email и статусу не "closed"
        open_tickets = Ticket.objects.filter(
            user_email=from_email, 
            status__in=['new', 'in_progress']  # status__in значит "статус в этом списке"
        ).order_by('-created_at')  # сортируем от новых к старым
        
        if open_tickets.exists():
            # Если нашли открытое обращение - используем его
            ticket = open_tickets.first()
            # Меняем статус на "в работе", если он был "новый"
            if ticket.status == 'new':
                ticket.status = 'in_progress'
                ticket.save()
            print(f"Добавлено сообщение в существующее обращение #{ticket.id}")
        else:
            # Если открытых обращений нет - создаем новое
            ticket = Ticket.objects.create(
                user_email=from_email,
                subject=subject or "Без темы",  # если темы нет - ставим "Без темы"
                status='new'
            )
            print(f"Создано новое обращение #{ticket.id}")
        
        # Добавляем сообщение от пользователя в обращение
        Message.objects.create(
            ticket=ticket,
            text=body,
            is_from_user=True  # это сообщение от пользователя, не от оператора
        )
        
        # Отправляем автоответ пользователю
        send_autoreply(from_email, ticket.id)
        
        return ticket
    
    except Exception as e:
        print(f"Ошибка обработки входящего письма: {e}")
        raise e
