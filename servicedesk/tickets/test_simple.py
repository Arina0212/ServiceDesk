# Тесты

from django.test import TestCase
from django.contrib.auth.models import User
from .models import Ticket, Message


class SimpleTicketTest(TestCase):
    """
    Простые тесты для проверки основной функциональности
    """

    def setUp(self):
        """
        Настройка тестовых данных перед каждым тестом
        """
        # Создаем тестового оператора
        self.test_operator = User.objects.create_user(
            username='operator',
            email='operator@test.com',
            password='testpass123'
        )

        # Создаем тестовое обращение
        self.test_ticket = Ticket.objects.create(
            user_email='user@example.com',
            subject='Тестовое обращение',
            status='new'
        )

    def test_ticket_status_change(self):
        """
        Тест 1: Проверяем, что статус обращения корректно изменяется
        """
        # Проверяем начальный статус
        self.assertEqual(self.test_ticket.status, 'new')

        # Меняем статус на "в работе"
        self.test_ticket.status = 'in_progress'
        self.test_ticket.assigned_to = self.test_operator
        self.test_ticket.save()

        # Проверяем, что статус изменился
        self.assertEqual(self.test_ticket.status, 'in_progress')
        self.assertEqual(self.test_ticket.assigned_to, self.test_operator)

        # Меняем статус на "закрыт"
        self.test_ticket.status = 'closed'
        self.test_ticket.save()

        # Проверяем финальный статус
        self.assertEqual(self.test_ticket.status, 'closed')

        print("Тест 1 пройден: Статус обращения изменяется корректно")

    def test_operator_message_creation(self):
        """
        Тест 2: Проверяем, что сообщение от оператора создается корректно
        """
        # Создаем сообщение от оператора
        operator_message = Message.objects.create(
            ticket=self.test_ticket,
            text='Здравствуйте! Мы получили ваше обращение и работаем над решением.',
            sender=self.test_operator,
            is_from_user=False  # Сообщение от оператора
        )

        # Проверяем, что сообщение создано
        self.assertIsNotNone(operator_message)

        # Проверяем поля сообщения
        self.assertEqual(operator_message.ticket, self.test_ticket)
        self.assertEqual(operator_message.sender, self.test_operator)
        self.assertEqual(operator_message.text,
                         'Здравствуйте! Мы получили ваше обращение и работаем над решением.')
        # Проверяем, что это НЕ от пользователя
        self.assertFalse(operator_message.is_from_user)

        # Проверяем, что сообщение связано с обращением
        messages = self.test_ticket.messages.all()
        self.assertEqual(messages.count(), 1)
        self.assertEqual(messages.first(), operator_message)

        print("Тест 2 пройден: Сообщение от оператора создается корректно")
