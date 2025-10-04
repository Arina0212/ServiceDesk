# tickets/admin.py
from django.contrib import admin
from .models import Ticket, Message


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """
    Настройки для отображения модели Ticket в админке.
    """
    # Поля, которые показываются в списке обращений
    list_display = ['id', 'subject', 'user_email',
                    'status', 'created_at', 'assigned_to']

    # Поля, по которым можно фильтровать
    list_filter = ['status', 'created_at', 'assigned_to']

    # Поля, по которым можно искать
    search_fields = ['subject', 'user_email', 'id']

    # Поля, которые можно редактировать прямо из списка
    list_editable = ['status', 'assigned_to']

    # Разбивка на страницы - по 20 обращений на страницу
    list_per_page = 20


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Настройки для отображения модели Message в админке.
    """
    # Поля, которые показываются в списке сообщений
    list_display = ['id', 'ticket', 'is_from_user', 'sender', 'created_at']

    # Поля, по которым можно фильтровать
    list_filter = ['is_from_user', 'created_at', 'ticket']

    # Поля, по которым можно искать
    search_fields = ['text', 'ticket__id']

    # Разбивка на страницы - по 30 сообщений на страницу
    list_per_page = 20

    """
        Когда оператор создает сообщение через админку, мы хотим автоматически указать, 
        что отправитель - это текущий пользователь. Если бы поле sender было в форме, 
        оператор мог бы выбрать любого пользователя, что неправильно
    """
    exclude = ['sender']

    def save_model(self, request, obj, form, change):
        """
        Автоматически сохраняем текущего пользователя как отправителя
        при создании нового сообщения.
        """
        if not obj.pk:  # Если объект создается, а не изменяется
            obj.sender = request.user
        super().save_model(request, obj, form, change)
