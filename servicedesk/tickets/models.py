from django.db import models
from django.contrib.auth.models import User

class Ticket(models.Model):
    """
    Эта модель хранит все обращения от пользователей.
    Здесь мы сохраняем email пользователя, тему обращения и его статус.
    """
    
    # Статусы для обращений
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('in_progress', 'В работе'),
        ('closed', 'Закрыт'),
    ]
    
    # Email пользователя, который написал нам
    user_email = models.EmailField(verbose_name='Email пользователя')
    
    # Тема обращения
    subject = models.CharField(max_length=255, verbose_name='Тема обращения')
    
    # Статус обращения (выбираем из вариантов выше)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='new',  # По умолчанию всегда "новый"
        verbose_name='Статус'
    )
    
    # Дата создания (ставится автоматически при создании)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    
    # Дата обновления (меняется сама при любом изменении)
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    
    # Кому поручили это обращение (может быть пустым)
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,  # Если удалим пользователя, здесь будет пусто
        null=True, 
        blank=True,
        related_name='assigned_tickets',  # Это чтобы потом можно было найти все обращения оператора
        verbose_name='Назначено на'
    )

    class Meta:
        # Как модель будет называться в админке
        verbose_name = 'Обращение'
        verbose_name_plural = 'Обращения'
        # Сортировка по умолчанию: сначала новые
        ordering = ['-created_at']

    def __str__(self):
        # Как будет выглядеть запись в админке и в shell
        return f"{self.subject} ({self.user_email}) - {self.get_status_display()}"


class Message(models.Model):
    """
    Эта модель для всех сообщений в рамках одного обращения.
    Здесь храним кто что написал и когда.
    """
    
    # Ссылка на обращение, к которому относится это сообщение
    ticket = models.ForeignKey(
        Ticket, 
        on_delete=models.CASCADE,  # Если удалим обращение, все сообщения тоже удалятся
        related_name='messages',  # Чтобы получить все сообщения обращения: ticket.messages.all()
        verbose_name='Обращение'
    )
    
    # Текст сообщения (может быть длинным)
    text = models.TextField(verbose_name='Текст сообщения')
    
    # Если отвечал оператор - сохраняем кто именно
    sender = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,  # Если удалим пользователя, здесь будет пусто
        null=True, 
        blank=True,
        verbose_name='Отправитель (оператор)'
    )
    
    # Отметка: сообщение от пользователя или от оператора
    is_from_user = models.BooleanField(
        default=False,  # По умолчанию False, значит от оператора
        verbose_name='От пользователя?'
    )
    
    # Дата создания сообщения (ставится автоматически)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        # Как модель будет называться в админке
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        # Сообщения по порядку: сначала старые
        ordering = ['created_at']

    def __str__(self):
        # Как будет выглядеть запись в админке и в shell
        if self.is_from_user:
            sender_info = "Пользователь"
        else:
            sender_info = f"Оператор {self.sender}"
        
        return f"{sender_info} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"