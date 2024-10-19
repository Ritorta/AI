import os # Импорт модуля os для работы с операционной системой
import time # Импорт модуля time для работы со временем
import requests # Импорт модуля requests для отправки HTTP запросов
import logging # Импорт модуля logging для логирования событий
import importlib.util # Импорт модуля importlib.util для импорта модуля из файла

# Импорта файла config.py
spec = importlib.util.spec_from_file_location("config", "C:/Users/Esdesu/Documents/Материалы по обучению/Обучение Ai/Folder_confing/config.py")
# Импорт модуля config из файла
config = importlib.util.module_from_spec(spec)
# Загрузка модуля config
spec.loader.exec_module(config)
# Получение ключа из модуля config
key_ai = config.key_ai

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Функция эмитации создания задания для сервиса prodia.com
def get_job(prompt, preset):
    # URL для отправки запроса
    url = "https://api.prodia.com/v1/sd/generate"

    # Данные для запроса
    payload = {
        "prompt": prompt,
        "upscale": True,
        "style_preset": f"{preset}"
    }

    # Заголовки запроса
    headers = {
        "accept": "application/json",
        "X-Prodia-Key": key_ai
    }

    # Обработка исключений при отправке запроса
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
    except requests.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err}')
        return None
    except Exception as err:
        logging.error(f'Other error occurred: {err}')
        return None

    # Получение JSON ответа
    res = response.json()
    # Извлечение ID задания из ответа
    res_job = res.get('job')
    # Логирование создания задания
    logging.info(f'Job created: {res_job}')
    return res_job

# Функция эмитации для получения URL изображения от сервиса prodia.com
def get_image_url(job):
    # Формирование URL для запроса информации о задании
    url = f"https://api.prodia.com/v1/job/{job}"

    # Заголовки запроса
    headers = {
        "accept": "application/json",
        "X-Prodia-Key": key_ai
    }

    # Обработка исключений при отправке запроса
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err}')
        return None, None
    except Exception as err:
        logging.error(f'Other error occurred: {err}')
        return None, None

    # Получение JSON ответа
    res = response.json()
    # Извлечение URL изображения из ответа
    url = res.get('imageUrl')
    # Извлечение статуса задания из ответа
    status = res.get('status')
    # Логирование URL изображения и статуса задания
    logging.info(f'Image URL: {url}, Status: {status}')
    return url, status

# Функция для сохранения изображения по URL(в идеале нафиг бы её переписать но время...)
def save_url(url, file_path):
    # Создание папки для сохранения изображения
    dir_image = os.path.join(os.path.dirname(__file__), 'folder_for_ai_image')
    os.makedirs(dir_image, exist_ok=True)

    # Определение имени и расширения файла
    base_name, ext = os.path.splitext(file_path)
    
    # Проверка наличия файла с таким же именем и начальна точка отсчёта для одинаковых(вышло хреново)
    i = 1
    while True:
        full_file_path = os.path.join(dir_image, f"{base_name}_{i}{ext}")
        if not os.path.exists(full_file_path):
            break
        i += 1

    # Обработка исключений при сохранении изображения
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
    except requests.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err}')
        return
    except Exception as err:
        logging.error(f'Other error occurred: {err}')
        return
    # Сохранение изображения
    with open(full_file_path, 'wb') as sv:
        for block in response.iter_content(1024):
            if not block:
                break
            sv.write(block)
    logging.info(f'Image saved as {file_path}')

# Функция для инициализации других функций
def start(prompt, preset):
    # Вызывает функцию get_job(prompt, preset) для создания задания для сервиса prodia.com и сохраняет возвращенный токен задания.
    token_name = get_job(prompt, preset)
    # Проверка успешности запуска, если нет, то записывает ошибку в лог и завершает функцию.
    if not token_name:
        logging.error('Failed to create job.')
        return
    
    #  Статусы заданий, используются для проверки готовности изображаенияя, чтобы избежать ошибки.
    status = 'generating'
    status_s = 'succeeded'

    # Запускает цикл, который будет повторяться до тех пор, пока статус задания указывает на то, что оно еще генерируется с таймаутом в 10 секунд.
    while status == 'generating':
        url, status = get_image_url(token_name)
        time.sleep(10)

    # Проверяет, если статус задания успешно завершен, тогда формирует путь к файлу, куда будет сохранено изображение, используя имя запроса как имя файла.
    if status == status_s:
        file_path = f'{prompt}.png'
        # Выводит URL изображения в консоль для проверки успешности получения.
        print(url)
        # вызывает функцию "save_url" для сохранения изображения по полученному URL.
        save_url(url, file_path)
    else:
        logging.error(f'Error: {status}')

    return url

# Запуск основной функции при запуске скрипта
if __name__ == '__main__':
    start('pony', 'name_preset')
