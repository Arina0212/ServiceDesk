from django.core.management.base import BaseCommand
from tickets.email_handler import process_incoming_email
import imaplib
import email
from email.header import decode_header
import os


class Command(BaseCommand):
    help = 'Проверяет Gmail на новые письма и обрабатывает их'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Выводить подробную информацию',
        )

    def handle(self, *args, **options):
        verbose = options['verbose']

        try:
            if verbose:
                self.stdout.write("Проверяем почту...")

            # Настройки из .env
            GEMAIL = os.getenv('EMAIL_HOST_USER')
            PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

            if not GEMAIL or not PASSWORD:
                self.stdout.write(
                    self.style.ERROR(
                        "Не настроены EMAIL_HOST_USER или EMAIL_HOST_PASSWORD в .env")
                )
                return

            # Подключаемся к Gmail
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(GEMAIL, PASSWORD)
            mail.select('inbox')

            # Ищем непрочитанные письма
            status, messages = mail.search(None, 'UNSEEN')
            email_ids = messages[0].split()

            if not email_ids:
                if verbose:
                    self.stdout.write("Новых писем нет")
                return

            self.stdout.write(f"Найдено {len(email_ids)} новых писем")

            processed_count = 0
            for e_id in email_ids:
                try:
                    # Получаем письмо
                    status, msg_data = mail.fetch(e_id, '(RFC822)')
                    raw_email = msg_data[0][1]

                    # Парсим письмо
                    msg = email.message_from_bytes(raw_email)

                    # Извлекаем тему
                    subject_header = decode_header(msg["Subject"])
                    subject = ""
                    for part, encoding in subject_header:
                        if isinstance(part, bytes):
                            subject += part.decode(
                                encoding if encoding else 'utf-8')
                        else:
                            subject += str(part)

                    # Извлекаем отправителя
                    from_email = msg["From"]
                    # Упрощаем email (может содержать имя <email>)
                    if '<' in from_email and '>' in from_email:
                        from_email = from_email.split('<')[1].split('>')[0]

                    # Извлекаем текст письма
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(
                                part.get("Content-Disposition"))

                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                try:
                                    body = part.get_payload(
                                        decode=True).decode()
                                    break
                                except:
                                    pass
                    else:
                        try:
                            body = msg.get_payload(decode=True).decode()
                        except:
                            body = msg.get_payload()

                    # Обрабатываем письмо
                    if verbose:
                        self.stdout.write(f"Обрабатываем письмо: {subject}")

                    ticket = process_incoming_email(from_email, subject, body)

                    # Помечаем как прочитанное
                    mail.store(e_id, '+FLAGS', '\\Seen')
                    processed_count += 1

                    if verbose:
                        self.stdout.write(
                            f"Письмо обработано, обращение #{ticket.id}")

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Ошибка обработки письма: {e}")
                    )
                    continue

            mail.close()
            mail.logout()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Проверка почты завершена. Обработано писем: {processed_count}")
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Ошибка подключения к почте: {e}")
            )
