# config/settings.py
import os
from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv  # ⬅️ ДОБАВЬТЕ ЭТО

# ⬅️ ДОБАВЬТЕ ЭТУ СТРОКУ - загружает .env файл
load_dotenv()

@dataclass
class BotConfig:
    TOKEN: str
    ADMIN_IDS: List[int]
    
    def __post_init__(self):
        # Валидация токена
        if not self.TOKEN or ':' not in self.TOKEN:
            raise ValueError("❌ Неверный формат BOT_TOKEN!")
        
        # Валидация ADMIN_IDS
        if not self.ADMIN_IDS:
            raise ValueError("❌ ADMIN_IDS не могут быть пустыми!")

@dataclass
class DatabaseConfig:
    DB_PATH: str

class Settings:
    def __init__(self):
        # Получение переменных окружения с валидацией
        self.BOT_TOKEN = self._get_required_env('BOT_TOKEN')
        self.ADMIN_IDS = self._get_admin_ids()
        self.DB_PATH = os.getenv('DB_PATH', 'bookings.db')
        self.EXPORT_DIR = os.getenv('EXPORT_DIR', 'exports')
        
        # Создание конфигов
        self.BOT_CONFIG = BotConfig(
            TOKEN=self.BOT_TOKEN,
            ADMIN_IDS=self.ADMIN_IDS
        )
        
        self.DB_CONFIG = DatabaseConfig(DB_PATH=self.DB_PATH)
    
    def _get_required_env(self, key: str) -> str:
        """Получить обязательную переменную окружения"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"❌ Переменная окружения {key} не установлена!")
        return value
    
    def _get_admin_ids(self) -> List[int]:
        """Получить список ID администраторов"""
        admin_ids_str = os.getenv('ADMIN_IDS', '')
        if not admin_ids_str:
            raise ValueError("❌ ADMIN_IDS не установлены!")
        
        try:
            return [int(id.strip()) for id in admin_ids_str.split(',')]
        except ValueError:
            raise ValueError("❌ ADMIN_IDS должны быть числами, разделенными запятыми!")

# Глобальная инициализация настроек
try:
    settings = Settings()
    BOT_CONFIG = settings.BOT_CONFIG
    DB_CONFIG = settings.DB_CONFIG
    print("✅ Настройки успешно загружены")
except Exception as e:
    print(f"❌ Ошибка загрузки настроек: {e}")
    raise