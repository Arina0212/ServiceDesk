# Добавляем обработчик вебхука для входящих писем

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .email_handler import process_incoming_email
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import Ticket, Message
from .forms import ReplyForm

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
    



@login_required  # Только для авторизованных пользователей
def ticket_list(request):
    """
    Страница со списком всех обращений.
    Можно фильтровать по статусу и сортировать.
    """
    # Получаем статус для фильтрации из параметров URL
    status_filter = request.GET.get('status', '')
    
    # Получаем все обращения
    tickets = Ticket.objects.all()
    
    # Фильтруем по статусу если выбран
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    
    # Сортируем по дате создания (новые сверху)
    tickets = tickets.order_by('-created_at')
    
    # Передаем данные в шаблон
    context = {
        'tickets': tickets,
        'status_filter': status_filter,
    }
    return render(request, 'tickets/ticket_list.html', context)

@login_required
def ticket_detail(request, ticket_id):
    """
    Страница с детальной информацией по обращению.
    Здесь можно отвечать пользователю и менять статус.
    """
    # Находим обращение или показываем 404 ошибку
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Форма для ответа пользователю
    form = ReplyForm()
    
    # Обработка ответа оператора
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            # Создаем новое сообщение от оператора
            message_text = form.cleaned_data['text']
            Message.objects.create(
                ticket=ticket,
                text=message_text,
                sender=request.user,  # Текущий пользователь
                is_from_user=False    # Сообщение от оператора
            )
            
            # Обновляем дату изменения обращения
            ticket.updated_at = timezone.now()
            ticket.save()
            
            # TODO: Здесь будет отправка email пользователю
            # пока просто редирект на эту же страницу
            return redirect('ticket_detail', ticket_id=ticket.id)
    
    # Получаем все сообщения этого обращения
    messages = ticket.messages.all().order_by('created_at')
    
    context = {
        'ticket': ticket,
        'messages': messages,
        'form': form,
    }
    return render(request, 'tickets/ticket_detail.html', context)

@login_required
def take_ticket(request, ticket_id):
    """
    Взять обращение в работу.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Назначаем обращение на текущего пользователя
    ticket.assigned_to = request.user
    ticket.status = 'in_progress'
    ticket.save()
    
    return redirect('ticket_detail', ticket_id=ticket.id)

@login_required
def close_ticket(request, ticket_id):
    """
    Закрыть обращение.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Меняем статус на закрытый
    ticket.status = 'closed'
    ticket.save()
    
    # TODO: Здесь будет отправка email о закрытии
    return redirect('ticket_list')
