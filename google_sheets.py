import gspread
from google.oauth2.service_account import Credentials
from typing import List, Optional
from datetime import datetime
import config


class GoogleSheetsManager:
    """Класс для работы с Google Sheets"""
    
    def __init__(self):
        """Инициализация менеджера Google Sheets"""
        self.credentials_file = config.GOOGLE_SHEETS_CREDENTIALS_FILE
        self.sheet_id = config.GOOGLE_SHEET_ID
        self.sheet_name = config.GOOGLE_SHEET_NAME
        
        # Настройка доступа к Google Sheets API
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = Credentials.from_service_account_file(
            self.credentials_file,
            scopes=scope
        )
        
        self.client = gspread.authorize(creds)
        self.sheet = None
        self._connect_to_sheet()
    
    def _connect_to_sheet(self):
        """Подключение к Google Sheet"""
        try:
            spreadsheet = self.client.open_by_key(self.sheet_id)
            try:
                self.sheet = spreadsheet.worksheet(self.sheet_name)
                # Проверяем, есть ли заголовки
                if self.sheet.row_count == 0 or not self.sheet.row_values(1):
                    self.sheet.append_row(['Дата', 'Время', 'Задача'])
            except gspread.exceptions.WorksheetNotFound:
                # Создаем лист, если его нет
                self.sheet = spreadsheet.add_worksheet(
                    title=self.sheet_name,
                    rows=1000,
                    cols=3
                )
                # Добавляем заголовки
                self.sheet.append_row(['Дата', 'Время', 'Задача'])
        except Exception as e:
            print(f"Ошибка при подключении к Google Sheet: {e}")
            raise
    
    def add_task(self, task_text: str) -> bool:
        """
        Добавляет задачу в Google Sheet
        
        Args:
            task_text: Текст задачи
            
        Returns:
            True если успешно, False в случае ошибки
        """
        try:
            now = datetime.now()
            date = now.strftime('%Y-%m-%d')
            time = now.strftime('%H:%M:%S')
            
            self.sheet.append_row([date, time, task_text])
            return True
        except Exception as e:
            print(f"Ошибка при добавлении задачи: {e}")
            return False
    
    def get_all_tasks(self) -> List[dict]:
        """
        Получает все задачи из Google Sheet
        
        Returns:
            Список словарей с задачами
        """
        try:
            # Получаем все записи (пропускаем заголовок)
            records = self.sheet.get_all_records()
            return records
        except Exception as e:
            print(f"Ошибка при получении задач: {e}")
            return []
    
    def format_tasks(self, tasks: List[dict]) -> str:
        """
        Форматирует список задач для красивого вывода
        
        Args:
            tasks: Список задач
            
        Returns:
            Отформатированная строка с задачами
        """
        if not tasks:
            return "📋 Список задач пуст"
        
        formatted_text = "📋 *Ваши задачи:*\n\n"
        
        for idx, task in enumerate(tasks, 1):
            date = task.get('Дата', 'N/A')
            time = task.get('Время', 'N/A')
            task_text = task.get('Задача', 'N/A')
            
            formatted_text += f"*{idx}.* 📅 {date} ⏰ {time}\n"
            formatted_text += f"   {task_text}\n\n"
        
        return formatted_text
