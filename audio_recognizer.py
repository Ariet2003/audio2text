import speech_recognition as sr
import os
from typing import Optional
from pydub import AudioSegment


class AudioRecognizer:
    """Класс для распознавания речи из аудио файлов"""
    
    def __init__(self, language: str = 'ru-RU'):
        """
        Инициализация распознавателя речи
        
        Args:
            language: Язык распознавания (по умолчанию русский)
        """
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 1
        self.language = language
    
    def _convert_to_wav(self, input_path: str, output_path: str) -> bool:
        """
        Конвертирует аудио файл в WAV формат
        
        Args:
            input_path: Путь к исходному файлу
            output_path: Путь для сохранения WAV файла
            
        Returns:
            True если успешно, False в случае ошибки
        """
        try:
            # Определяем формат по расширению
            file_ext = os.path.splitext(input_path)[1].lower()
            
            # Загружаем аудио файл
            if file_ext == '.ogg':
                audio = AudioSegment.from_ogg(input_path)
            elif file_ext == '.mp3':
                audio = AudioSegment.from_mp3(input_path)
            elif file_ext == '.m4a':
                audio = AudioSegment.from_file(input_path, format='m4a')
            else:
                # Пытаемся определить формат автоматически
                audio = AudioSegment.from_file(input_path)
            
            # Экспортируем в WAV (моно, 16kHz - оптимально для распознавания)
            audio = audio.set_channels(1)  # Моно
            audio = audio.set_frame_rate(16000)  # 16kHz
            audio.export(output_path, format='wav')
            
            return True
        except Exception as e:
            print(f"Ошибка при конвертации аудио: {e}")
            return False
    
    def recognize_from_file(self, audio_file_path: str) -> Optional[str]:
        """
        Распознает речь из аудио файла
        
        Args:
            audio_file_path: Путь к аудио файлу
            
        Returns:
            Распознанный текст или None в случае ошибки
        """
        wav_path = None
        try:
            # Проверяем формат файла
            file_ext = os.path.splitext(audio_file_path)[1].lower()
            
            # Если файл не WAV, конвертируем его
            if file_ext != '.wav':
                wav_path = audio_file_path.rsplit('.', 1)[0] + '.wav'
                if not self._convert_to_wav(audio_file_path, wav_path):
                    return None
                audio_file_path = wav_path
            
            # Распознавание речи
            with sr.AudioFile(audio_file_path) as source:
                # Подстройка под окружающий шум
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # Чтение аудио файла
                audio = self.recognizer.record(source)
            
            # Распознавание с помощью Google Speech Recognition
            text = self.recognizer.recognize_google(
                audio_data=audio,
                language=self.language
            )
            
            return text.lower()
        
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"Ошибка при запросе к сервису распознавания: {e}")
            return None
        except Exception as e:
            print(f"Неожиданная ошибка при распознавании: {e}")
            return None
        finally:
            # Удаляем временный WAV файл, если он был создан
            if wav_path and os.path.exists(wav_path):
                try:
                    os.remove(wav_path)
                except:
                    pass
