# tickets/email_service.py
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

def send_operator_reply(ticket, message_text, operator_name):
    """
    Отправляет ответ оператора пользователю
    """
    subject = f"Re: {ticket.subject} [#{ticket.id}]"
    
    # Красивое оформление письма в HTML
    html_message = render_to_string('tickets/email_operator_reply.html', {
        'ticket': ticket,
        'message_text': message_text,
        'operator_name': operator_name,
    })
    
    # Простой текст для почтовых клиентов
    plain_message = f"""
    Здравствуйте!
    
    Оператор {operator_name} ответил на ваше обращение "{ticket.subject}":
    
    {message_text}
    
    ---
    Номер обращения: #{ticket.id}
    Статус: {ticket.get_status_display()}
    
    Вы можете ответить на это письмо, и ваше сообщение будет добавлено к обращению.
    
    С уважением,
    Служба поддержки ServiceDesk
    """
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,  # HTML версия
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[ticket.user_email],
            fail_silently=False,
        )
        print(f"Ответ оператора отправлен на {ticket.user_email}")
        return True
    except Exception as e:
        print(f"Ошибка отправки ответа: {e}")
        return False

def send_ticket_closed_notification(ticket):
    """
    Отправляет уведомление о закрытии обращения
    """
    subject = f"Ваше обращение #{ticket.id} закрыто"
    
    html_message = render_to_string('tickets/email_ticket_closed.html', {
        'ticket': ticket,
    })
    
    plain_message = f"""
    Здравствуйте!
    
    Ваше обращение "{ticket.subject}" было закрыто.
    
    Номер обращения: #{ticket.id}
    Статус: Закрыто
    
    Если проблема не решена, вы можете создать новое обращение.
    
    С уважением,
    Служба поддержки ServiceDesk
    """
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[ticket.user_email],
            fail_silently=False,
        )
        print(f"Уведомление о закрытии отправлено на {ticket.user_email}")
        return True
    except Exception as e:
        print(f"Ошибка отправки уведомления: {e}")
        return False
    
def send_autoreply(to_email, ticket_id):
    """
    Отправляет автоматический ответ пользователю
    """
    subject = f"Ваше обращение #{ticket_id} принято в работу"
    html_message = render_to_string('tickets/email_autoreply.html', {
        'ticket': ticket_id,
    })
    
    message = f"""
    Здравствуйте!
    
    Мы получили ваше обращение и уже начали его обработку.
    Номер вашего обращения: #{ticket_id}
    
    Наши операторы свяжутся с вами в ближайшее время.
    
    С уважением,
    Служба поддержки
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Ошибка отправки уведомления: {e}")
        return False