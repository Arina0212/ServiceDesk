# check_emails.py
import imaplib
import email
from email.header import decode_header
import os
import django
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tickets.email_handler import process_incoming_email

def check_emails():
    """
    Проверяет Gmail на новые письма и обрабатывает их.
    """
    try:
        print("Проверяем почту...")
        
        # Настройки из .env
        GEMAIL = os.getenv('EMAIL_HOST_USER')
        PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
        
        if not GEMAIL or not PASSWORD:
            print("Не настроены GMAIL_EMAIL или GMAIL_APP_PASSWORD в .env")
            return
        
        # Подключаемся к Gmail
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(GEMAIL, PASSWORD)
        mail.select('inbox')
        
        # Ищем непрочитанные письма
        status, messages = mail.search(None, 'UNSEEN')
        email_ids = messages[0].split()
        
        if not email_ids:
            print("Новых писем нет")
            return
        
        print(f"Найдено {len(email_ids)} новых писем")
        
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
                        subject += part.decode(encoding if encoding else 'utf-8')
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
                        content_disposition = str(part.get("Content-Disposition"))
                        
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            try:
                                body = part.get_payload(decode=True).decode()
                                break
                            except:
                                pass
                else:
                    try:
                        body = msg.get_payload(decode=True).decode()
                    except:
                        body = msg.get_payload()
                
                # Обрабатываем письмо
                print(f"Обрабатываем письмо: {subject}")
                ticket = process_incoming_email(from_email, subject, body)
                
                # Помечаем как прочитанное
                mail.store(e_id, '+FLAGS', '\\Seen')
                print(f"Письмо обработано, обращение #{ticket.id}")
                
            except Exception as e:
                print(f"Ошибка обработки письма: {e}")
                continue
        
        mail.close()
        mail.logout()
        print("Проверка почты завершена")
        
    except Exception as e:
        print(f"Ошибка подключения к почте: {e}")

if __name__ == '__main__':
    check_emails()