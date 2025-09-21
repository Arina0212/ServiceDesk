# Добавляем обработчик вебхука для входящих писем

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .email_handler import process_incoming_email

@csrf_exempt  # Отключаем CSRF защиту для этого view (для внешних сервисов)
@require_http_methods(["POST"])  # Разрешаем только POST запросы
def inbound_email_webhook(request):
    """
    Обрабатывает вебхук от почтового сервиса (например, SendGrid)
    """
    try:
        # Парсим JSON из тела запроса
        data = json.loads(request.body)
        
        # Извлекаем данные письма (зависит от формата SendGrid)
        from_email = data.get('from')
        subject = data.get('subject')
        body = data.get('text') or data.get('html', '')
        
        # Обрабатываем письмо
        ticket = process_incoming_email(from_email, subject, body)
        
        # Возвращаем успешный ответ
        return JsonResponse({
            'status': 'success', 
            'ticket_id': ticket.id,
            'message': 'Email processed successfully'
        })
        
    except Exception as e:
        # Если что-то пошло не так - возвращаем ошибку
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)