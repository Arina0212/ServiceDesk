"""
Прямая проверка почты без использования Django команд
"""

import os
import sys
import time
import threading
import django
from datetime import datetime
import imaplib
import email
from email.header import decode_header

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tickets.email_handler import process_incoming_email

class DirectEmailChecker:
    def __init__(self):
        self.running = False
        self.thread = None
    
    def check_emails_once(self):
        """Выполняет одну проверку почты"""
        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Проверка почты...")
            
            # Настройки из .env
            GEMAIL = os.getenv('EMAIL_HOST_USER')
            PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
            
            if not GEMAIL or not PASSWORD:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Ошибка: Не настроены EMAIL_HOST_USER или EMAIL_HOST_PASSWORD в .env")
                return
            
            # Подключаемся к Gmail
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(GEMAIL, PASSWORD)
            mail.select('inbox')
            
            # Ищем непрочитанные письма
            status, messages = mail.search(None, 'UNSEEN')
            email_ids = messages[0].split()
            
            if not email_ids:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Новых писем нет")
                mail.close()
                mail.logout()
                return
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Найдено {len(email_ids)} новых писем")
            
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
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Обрабатываем письмо: {subject}")
                    
                    ticket = process_incoming_email(from_email, subject, body)
                    
                    # Помечаем как прочитанное
                    mail.store(e_id, '+FLAGS', '\\Seen')
                    processed_count += 1
                    
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Письмо обработано, обращение #{ticket.id}")
                    
                except Exception as e:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Ошибка обработки письма: {e}")
                    continue
            
            mail.close()
            mail.logout()
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Проверка завершена. Обработано писем: {processed_count}")
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Ошибка: {e}")
    
    def run_periodically(self):
        """Запускает периодическую проверку"""
        while self.running:
            self.check_emails_once()
            # Ждем 10 секунд
            for _ in range(10):
                if not self.running:
                    break
                time.sleep(1)
    
    def start(self):
        """Запускает автоматическую проверку"""
        if self.running:
            print("Проверка уже запущена!")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self.run_periodically)
        self.thread.daemon = True
        self.thread.start()
        
        print("Автоматическая проверка почты запущена!")
        print("Проверка будет выполняться каждые 10 секунд")
        print("Для остановки нажмите Ctrl+C")
    
    def stop(self):
        """Останавливает автоматическую проверку"""
        if not self.running:
            print("Проверка не запущена!")
            return
        
        self.running = False
        if self.thread:
            self.thread.join()
        print("Автоматическая проверка остановлена!")

def main():
    """Основная функция"""
    checker = DirectEmailChecker()
    
    try:
        checker.start()
        
        # Основной цикл - ждем сигнала остановки
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nПолучен сигнал остановки...")
        checker.stop()
        print("Программа завершена")

if __name__ == '__main__':
    main()
