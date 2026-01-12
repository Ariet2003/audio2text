import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import config
from audio_recognizer import AudioRecognizer
from google_sheets import GoogleSheetsManager


# Инициализация бота и диспетчера
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Инициализация сервисов
audio_recognizer = AudioRecognizer(language='ru-RU')
sheets_manager = GoogleSheetsManager()


# Состояния FSM
class TaskStates(StatesGroup):
    waiting_for_audio = State()


# Создание клавиатуры с кнопками
def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Создает главную клавиатуру с кнопками"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Добавить задачу")],
            [KeyboardButton(text="📋 Посмотреть задачи")],
            [KeyboardButton(text="🔗 Ссылка на Google sheet")]
        ],
        resize_keyboard=True
    )
    return keyboard


@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    welcome_text = (
        "👋 Привет! Я бот для управления задачами.\n\n"
        "Я могу:\n"
        "• Принимать аудио файлы и преобразовывать их в задачи\n"
        "• Показывать все ваши задачи\n"
        "• Предоставлять ссылку на Google Sheet\n\n"
        "Выберите действие из меню ниже:"
    )
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard()
    )


@dp.message(lambda message: message.text == "➕ Добавить задачу")
async def add_task_handler(message: Message, state: FSMContext):
    """Обработчик кнопки 'Добавить задачу'"""
    await state.set_state(TaskStates.waiting_for_audio)
    await message.answer(
        "🎤 Пожалуйста, отправьте аудио файл с вашей задачей.\n"
        "Я распознаю речь и добавлю задачу в Google Sheet."
    )


@dp.message(lambda message: message.text == "📋 Посмотреть задачи")
async def view_tasks_handler(message: Message):
    """Обработчик кнопки 'Посмотреть задачи'"""
    try:
        tasks = sheets_manager.get_all_tasks()
        formatted_tasks = sheets_manager.format_tasks(tasks)
        await message.answer(
            formatted_tasks,
            parse_mode="Markdown"
        )
    except Exception as e:
        await message.answer(
            f"❌ Произошла ошибка при получении задач: {e}"
        )


@dp.message(lambda message: message.text == "🔗 Ссылка на Google sheet")
async def sheet_link_handler(message: Message):
    """Обработчик кнопки 'Ссылка на Google sheet'"""
    link = config.GOOGLE_SHEET_LINK
    if link:
        await message.answer(
            f"🔗 Ссылка на Google Sheet:\n{link}"
        )
    else:
        await message.answer(
            "❌ Ссылка на Google Sheet не настроена. "
            "Пожалуйста, настройте GOOGLE_SHEET_LINK в конфигурации."
        )


@dp.message(TaskStates.waiting_for_audio)
async def process_audio(message: Message, state: FSMContext):
    """Обработчик аудио файлов"""
    # Проверяем, что это аудио файл
    if not message.audio and not message.voice:
        await message.answer(
            "❌ Пожалуйста, отправьте аудио файл (voice message или audio file).\n"
            "Я могу распознать только аудио файлы."
        )
        return
    
    # Отправляем сообщение о начале обработки
    processing_msg = await message.answer("🔄 Обрабатываю аудио файл...")
    
    try:
        # Определяем тип файла и получаем file_id
        if message.voice:
            file_id = message.voice.file_id
        else:
            file_id = message.audio.file_id
        
        # Получаем информацию о файле
        file_info = await bot.get_file(file_id)
        
        # Скачиваем файл
        file_path = file_info.file_path
        
        # Определяем расширение файла
        file_ext = os.path.splitext(file_path)[1] or '.ogg'
        
        # Сохраняем во временный файл
        temp_file_path = f"temp_audio_{message.from_user.id}{file_ext}"
        
        # Скачиваем и сохраняем файл
        # В Aiogram 3.x download_file возвращает корутину, которую нужно await
        downloaded_file = await bot.download_file(file_path)
        
        # Читаем содержимое файла (read() - синхронный метод)
        file_content = downloaded_file.read()
        
        # Сохраняем во временный файл
        with open(temp_file_path, 'wb') as f:
            f.write(file_content)
        
        try:
            # Распознаем аудио
            recognized_text = audio_recognizer.recognize_from_file(temp_file_path)
        finally:
            # Удаляем временный файл после распознавания
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except:
                    pass
        
        if not recognized_text:
            await processing_msg.edit_text(
                "❌ Не удалось распознать речь из аудио файла. "
                "Пожалуйста, попробуйте еще раз с более четкой записью."
            )
            await state.clear()
            return
        
        # Добавляем задачу в Google Sheet
        success = sheets_manager.add_task(recognized_text)
        
        if success:
            await processing_msg.edit_text(
                f"✅ Задача добавлена!\n\n"
                f"📝 Текст задачи: *{recognized_text}*",
                parse_mode="Markdown"
            )
        else:
            await processing_msg.edit_text(
                "❌ Не удалось добавить задачу в Google Sheet. "
                "Пожалуйста, попробуйте позже."
            )
        
        await state.clear()
        
    except Exception as e:
        # Удаляем временный файл в случае ошибки
        # Пробуем удалить файлы с разными расширениями
        for ext in ['.ogg', '.wav', '.mp3', '.m4a']:
            temp_file_path = f"temp_audio_{message.from_user.id}{ext}"
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except:
                    pass
        
        await processing_msg.edit_text(
            f"❌ Произошла ошибка при обработке аудио: {str(e)}"
        )
        await state.clear()


@dp.message()
async def default_handler(message: Message, state: FSMContext):
    """Обработчик всех остальных сообщений"""
    current_state = await state.get_state()
    
    if current_state == TaskStates.waiting_for_audio:
        await message.answer(
            "❌ Пожалуйста, отправьте аудио файл (voice message или audio file)."
        )
    else:
        await message.answer(
            "👋 Используйте кнопки меню для взаимодействия с ботом.",
            reply_markup=get_main_keyboard()
        )


async def main():
    """Главная функция для запуска бота"""
    print("🤖 Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
